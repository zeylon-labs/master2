from tools.core import generate_private_key, generate_public_key, sign_csr


class CertificateAuthority:
    def __init__(self, config, password, private_key_filename, public_key_filename):
        self._private_key = generate_private_key(private_key_filename, password)
        self.certificate = generate_public_key(self._private_key, public_key_filename, config)

    def sign(self, csr, certificate_filename):
        sign_csr(csr, self.certificate, self._private_key, certificate_filename)
