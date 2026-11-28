from tools.core import generate_csr, generate_private_key


class Server:
    def __init__(self, config, password, private_key_filename, csr_filename):
        private_key = generate_private_key(private_key_filename, password)
        self._csr = generate_csr(private_key, csr_filename, config)

    def get_csr(self):
        return self._csr
