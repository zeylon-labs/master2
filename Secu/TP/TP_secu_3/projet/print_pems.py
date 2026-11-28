import argparse
from pathlib import Path

import pem
from cryptography import x509
from cryptography.hazmat.primitives import hashes

from tools.paths import CA_CERT, DEFAULT_RESOURCES, SERVER_CERT


def print_pems(filename):
    path = Path(filename)
    block, = pem.parse_file(str(path))
    cert = x509.load_pem_x509_certificate(block.as_bytes())
    print(path.name, "· PEM", type(block).__name__)
    print("Sujet       ", cert.subject.rfc4514_string())
    print("Émetteur    ", cert.issuer.rfc4514_string())
    print("Série       ", format(cert.serial_number, "x"))
    print("Validité UTC", cert.not_valid_before_utc.isoformat(), "/", cert.not_valid_after_utc.isoformat())
    print("Autorité    ", cert.extensions.get_extension_for_class(x509.BasicConstraints).value.ca)
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        print("SAN DNS     ", ", ".join(san.get_values_for_type(x509.DNSName)))
    except x509.ExtensionNotFound:
        pass
    print("SHA-256     ", cert.fingerprint(hashes.SHA256()).hex(), end="\n\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Afficher les deux certificats X.509 du club")
    parser.add_argument("--resources", type=Path, default=DEFAULT_RESOURCES)
    args = parser.parse_args()
    for filename in (CA_CERT, SERVER_CERT):
        print_pems(args.resources / filename)
