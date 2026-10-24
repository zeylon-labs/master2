"""Tests X509 sur certificats locaux de test, sans accès au réseau."""
from datetime import datetime, timedelta, timezone
import unittest
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from observer_certificat import analyser_der


class Certificat(unittest.TestCase):
    def fabriquer(self, publique, emetteur):
        nom = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test.local")])
        maintenant = datetime.now(timezone.utc)
        certificat = (x509.CertificateBuilder().subject_name(nom).issuer_name(nom)
            .public_key(publique).serial_number(1234)
            .not_valid_before(maintenant - timedelta(minutes=1))
            .not_valid_after(maintenant + timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName("test.local")]), critical=False)
            .sign(emetteur, hashes.SHA256()))
        return analyser_der(certificat.public_bytes(serialization.Encoding.DER))

    def test_rsa(self):
        cle = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        donnees = self.fabriquer(cle.public_key(), cle)
        self.assertEqual(donnees["cle_publique_algorithme"], "RSA")
        self.assertEqual(donnees["cle_publique_bits"], 2048)
        self.assertEqual(donnees["exposant_public_rsa"], 65537)
        self.assertEqual(donnees["empreinte_utilisee_dans_signature"], "sha256")
        self.assertIn("PKCS1", donnees["bourrage_signature_certificat"])

    def test_ec(self):
        cle = ec.generate_private_key(ec.SECP256R1())
        donnees = self.fabriquer(cle.public_key(), cle)
        self.assertEqual(donnees["cle_publique_bits"], 256)
        self.assertIsNone(donnees["exposant_public_rsa"])
        self.assertIn("ECDSA", donnees["bourrage_signature_certificat"])

    def test_cle_ec_certificat_signe_rsa(self):
        publique = ec.generate_private_key(ec.SECP256R1()).public_key()
        emetteur = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        donnees = self.fabriquer(publique, emetteur)
        self.assertIn("EC", donnees["cle_publique_algorithme"])
        self.assertIn("PKCS1", donnees["bourrage_signature_certificat"])
        self.assertIsNone(donnees["exposant_public_rsa"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
