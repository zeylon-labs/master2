from contextlib import contextmanager, redirect_stdout
from dataclasses import replace
from datetime import datetime, timezone
import http.client
import http.cookiejar
import io
import json
from pathlib import Path
import ssl
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import build_opener, HTTPCookieProcessor, HTTPSHandler, ProxyHandler

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from werkzeug.security import check_password_hash
from werkzeug.serving import make_server

from build import CA, SERVER, build
from ca.core import CertificateAuthority
from print_pems import print_pems
from run_server import create_account, create_app, server_context
from server.core import Server


@contextmanager
def listen(app, context=None):
    server = make_server("127.0.0.1", 0, app, ssl_context=context)
    thread = Thread(target=server.serve_forever)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


def certificate(path):
    return x509.load_pem_x509_certificate(path.read_bytes())


class TestCertificats(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp = TemporaryDirectory()
        cls.addClassCleanup(temp.cleanup)
        cls.directory = Path(temp.name)
        build(cls.directory, "ca-test", "serveur-test")

    def test_generation_independante(self):
        expected = {"ca-private-key.pem", "ca-public-key.pem", "server-private-key.pem",
                    "server-csr.pem", "server-public-key.pem"}
        self.assertEqual({p.name for p in self.directory.iterdir()}, expected)
        first = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        with self.assertRaises(FileExistsError):
            build(self.directory, "autre-ca", "autre-serveur")
        self.assertEqual(first, {p.name: p.read_bytes() for p in self.directory.iterdir()})
        with TemporaryDirectory() as other:
            second = Path(other)
            build(second, "ca-2", "serveur-2")
            self.assertEqual({p.name for p in second.iterdir()}, expected)
            ca2 = certificate(second / "ca-public-key.pem")
            server2 = certificate(second / "server-public-key.pem")
            server2.verify_directly_issued_by(ca2)
            for name in ("ca-public-key.pem", "server-public-key.pem"):
                self.assertNotEqual(certificate(self.directory / name).public_key().public_numbers(),
                                    certificate(second / name).public_key().public_numbers())

    def test_cles_chiffrees(self):
        for role, password, wrong in (("ca", b"ca-test", b"serveur-test"),
                                      ("server", b"serveur-test", b"ca-test")):
            with self.subTest(role=role):
                data = (self.directory / f"{role}-private-key.pem").read_bytes()
                self.assertIn(b"BEGIN ENCRYPTED PRIVATE KEY", data)
                with self.assertRaises(ValueError):
                    serialization.load_pem_private_key(data, wrong)
                key = serialization.load_pem_private_key(data, password)
                cert = certificate(self.directory / f"{role}-public-key.pem")
                self.assertEqual(key.key_size, 2048)
                self.assertEqual(key.public_key().public_numbers(), cert.public_key().public_numbers())

    def test_autorite_et_validite(self):
        ca = certificate(self.directory / "ca-public-key.pem")
        ca.verify_directly_issued_by(ca)
        self.assertEqual(ca.subject, ca.issuer)
        self.assertEqual(ca.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
                         "Autorité du Club des Ormes")
        constraints = ca.extensions.get_extension_for_class(x509.BasicConstraints)
        self.assertTrue(constraints.critical and constraints.value.ca)
        self.assertTrue(ca.extensions.get_extension_for_class(x509.KeyUsage).value.key_cert_sign)
        now = datetime.now(timezone.utc)
        for item in (ca, certificate(self.directory / "server-public-key.pem")):
            self.assertLessEqual(item.not_valid_before_utc, now)
            self.assertGreater(item.not_valid_after_utc, now)

    def test_csr_et_signature(self):
        ca = certificate(self.directory / "ca-public-key.pem")
        server = certificate(self.directory / "server-public-key.pem")
        csr = x509.load_pem_x509_csr((self.directory / "server-csr.pem").read_bytes())
        key = serialization.load_pem_private_key((self.directory / "server-private-key.pem").read_bytes(),
                                                 b"serveur-test")
        self.assertTrue(csr.is_signature_valid)
        self.assertEqual(csr.public_key().public_numbers(), key.public_key().public_numbers())
        self.assertEqual(server.public_key().public_numbers(), csr.public_key().public_numbers())
        self.assertEqual(server.subject, csr.subject)
        self.assertEqual(server.issuer, ca.subject)
        server.verify_directly_issued_by(ca)
        self.assertFalse(server.extensions.get_extension_for_class(x509.BasicConstraints).value.ca)
        self.assertIn(ExtendedKeyUsageOID.SERVER_AUTH, server.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value)
        for item in (csr, server):
            san = item.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
            self.assertEqual(list(san), [x509.DNSName("localhost")])

    def test_autre_nom_refuse(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            authority = CertificateAuthority(CA, "exemple-ca", root / "ca.key", root / "ca.crt")
            server = Server(replace(SERVER, alt_names=("autre.invalid",)), "exemple-serveur",
                            root / "serveur.key", root / "demande.csr")
            with self.assertRaisesRegex(ValueError, "localhost"):
                authority.sign(server.get_csr(), root / "serveur.crt")
            self.assertFalse((root / "serveur.crt").exists())

    def test_visualisation(self):
        for filename, role in (("ca-public-key.pem", "True"), ("server-public-key.pem", "False")):
            with self.subTest(filename=filename):
                path = self.directory / filename
                output = io.StringIO()
                with redirect_stdout(output):
                    print_pems(path)
                text = output.getvalue()
                self.assertIn(filename + " · PEM Certificate", text)
                self.assertIn(format(certificate(path).serial_number, "x"), text)
                self.assertIn("Autorité     " + role, text)
                if role == "False":
                    self.assertIn("SAN DNS      localhost", text)


class TestService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp = TemporaryDirectory()
        cls.addClassCleanup(temp.cleanup)
        cls.directory = Path(temp.name)
        build(cls.directory, "ca-test", "serveur-test")
        cls.protected_message = "Orme-du-test"
        cls.password = "Mot-de-passe-test-compte"
        create_account(cls.directory, "membre", cls.password, cls.protected_message)
        cls.account = json.loads((cls.directory / "compte.json").read_text(encoding="utf-8"))
        cls.tls = server_context(cls.directory, "serveur-test")
        cls.client_tls = ssl.create_default_context(cafile=str(cls.directory / "ca-public-key.pem"))

    def test_http(self):
        with listen(create_app()) as port:
            conn = http.client.HTTPConnection("127.0.0.1", port, timeout=3)
            try:
                conn.request("GET", "/")
                response = conn.getresponse()
                self.assertEqual(response.status, 200)
                self.assertIn(b"Silex-Lilas-28", response.read())
            finally:
                conn.close()

    def test_confiance_et_nom(self):
        unknown_ca = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        with listen(create_app(self.account), self.tls) as port:
            for host, trust, errors in (("localhost", unknown_ca, (20, 21)),
                                        ("127.0.0.1", self.client_tls, (62, 64))):
                with self.subTest(host=host):
                    conn = http.client.HTTPSConnection(host, port, context=trust, timeout=3)
                    try:
                        with self.assertRaises(ssl.SSLCertVerificationError) as caught:
                            conn.request("GET", "/")
                        self.assertIn(caught.exception.verify_code, errors)
                        print(f"{host} : {caught.exception.verify_message}")
                    finally:
                        conn.close()
            conn = http.client.HTTPSConnection("localhost", port, context=self.client_tls, timeout=3)
            try:
                conn.request("GET", "/")
                self.assertEqual(conn.getresponse().status, 401)
            finally:
                conn.close()

    def test_stockage_scrypt(self):
        stored = (self.directory / "compte.json").read_text(encoding="utf-8")
        self.assertNotIn(self.password, stored)
        digest = self.account["password_hash"]
        method, salt, _ = digest.split("$")
        self.assertEqual(method, "scrypt:32768:8:3")
        self.assertGreaterEqual(len(salt), 16)
        self.assertTrue(check_password_hash(digest, self.password))
        self.assertFalse(check_password_hash(digest, "incorrect"))
        with TemporaryDirectory() as temp:
            create_account(Path(temp), "membre", self.password, "Autre mois")
            copy = json.loads((Path(temp) / "compte.json").read_text(encoding="utf-8"))
            self.assertNotEqual(copy["password_hash"].split("$")[1], salt)
        with self.assertRaises(FileExistsError):
            create_account(self.directory, "nouveau", "autre", "Autre mois")
        self.assertEqual(stored, (self.directory / "compte.json").read_text(encoding="utf-8"))

    def test_acces_et_deconnexion(self):
        cookies = http.cookiejar.CookieJar()
        browser = build_opener(ProxyHandler({}), HTTPSHandler(context=self.client_tls), HTTPCookieProcessor(cookies))
        with listen(create_app(self.account), self.tls) as port:
            base = f"https://localhost:{port}"

            def refused(route, data=None):
                with self.assertRaises(HTTPError) as caught:
                    browser.open(base + route, data, timeout=3)
                with caught.exception as response:
                    self.assertEqual(response.code, 401)
                    body = response.read().decode()
                    self.assertNotIn(self.protected_message, body)
                    return body

            self.assertIn("Connexion membre", refused("/"))
            for user, password in (("membre", "incorrect"), ("inconnu", self.password)):
                form = urlencode({"username": user, "password": password}).encode()
                self.assertIn("Identifiant ou mot de passe incorrect", refused("/connexion", form))
                refused("/")
            form = urlencode({"username": "membre", "password": self.password}).encode()
            with browser.open(base + "/connexion", form, timeout=3) as response:
                self.assertEqual(response.status, 200)
                self.assertEqual(response.url, base + "/")
                self.assertIn(self.protected_message, response.read().decode())
                self.assertEqual(response.headers["Cache-Control"], "no-store")
            session_cookie, = cookies
            self.assertTrue(session_cookie.secure)
            self.assertTrue(session_cookie.has_nonstandard_attr("HttpOnly"))
            refused("/deconnexion", b"")
            self.assertEqual(len(cookies), 0)
            refused("/")


if __name__ == "__main__":
    unittest.main()
