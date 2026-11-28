"""Opérations X.509 du squelette du TP LUSS01."""
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


@dataclass(frozen=True)
class Configuration:
    country: str
    state: str
    locality: str
    org: str
    hostname: str
    alt_names: tuple[str, ...] = ()


def read_configuration(config):
    return x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, config.country),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, config.state),
        x509.NameAttribute(NameOID.LOCALITY_NAME, config.locality),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, config.org),
        x509.NameAttribute(NameOID.COMMON_NAME, config.hostname),
    ])


def generate_private_key(filename, password):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    Path(filename).write_bytes(key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
        serialization.BestAvailableEncryption(password.encode("utf-8")),
    ))
    return key


def certificate_builder(subject, issuer, public_key, valid_until=None):
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=60)
    return (x509.CertificateBuilder()
            .subject_name(subject).issuer_name(issuer).public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now).not_valid_after(min(end, valid_until) if valid_until else end)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False))


def generate_public_key(private_key, filename, config):
    subject = read_configuration(config)
    usage = x509.KeyUsage(digital_signature=False, content_commitment=False, key_encipherment=False,
                          data_encipherment=False, key_agreement=False, key_cert_sign=True,
                          crl_sign=True, encipher_only=False, decipher_only=False)
    builder = (certificate_builder(subject, subject, private_key.public_key())
               .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
               .add_extension(usage, critical=True))
    certificate = builder.sign(private_key, hashes.SHA256())
    Path(filename).write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
    return certificate


def generate_csr(private_key, filename, config):
    names = x509.SubjectAlternativeName([x509.DNSName(name) for name in config.alt_names])
    csr = (x509.CertificateSigningRequestBuilder().subject_name(read_configuration(config))
           .add_extension(names, critical=False).sign(private_key, hashes.SHA256()))
    Path(filename).write_bytes(csr.public_bytes(serialization.Encoding.PEM))
    return csr


def sign_csr(csr, ca_certificate, ca_private_key, filename):
    if not csr.is_signature_valid:
        raise ValueError("La signature de la demande est invalide.")
    # Le TP délivre un certificat serveur pour le seul nom utilisé dans l’URL.
    names = csr.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    if list(names) != [x509.DNSName("localhost")]:
        raise ValueError("Seul le nom DNS localhost est autorisé pour ce TP.")
    usage = x509.KeyUsage(digital_signature=True, content_commitment=False, key_encipherment=True,
                          data_encipherment=False, key_agreement=False, key_cert_sign=False,
                          crl_sign=False, encipher_only=False, decipher_only=False)
    builder = (certificate_builder(csr.subject, ca_certificate.subject, csr.public_key(),
                                   ca_certificate.not_valid_after_utc)
               .add_extension(names, critical=False)
               .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
               .add_extension(usage, critical=True)
               .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
               .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(
                   ca_private_key.public_key()), critical=False))
    certificate = builder.sign(ca_private_key, hashes.SHA256())
    Path(filename).write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
