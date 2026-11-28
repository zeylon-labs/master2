from getpass import getpass
from pathlib import Path
import os


DEFAULT_RESOURCES = Path(__file__).resolve().parents[1] / "resources"
CA_KEY = "ca-private-key.pem"
CA_CERT = "ca-public-key.pem"
SERVER_KEY = "server-private-key.pem"
SERVER_CSR = "server-csr.pem"
SERVER_CERT = "server-public-key.pem"
PEM_FILES = (CA_KEY, CA_CERT, SERVER_KEY, SERVER_CSR, SERVER_CERT)
ACCOUNT = "compte.json"


def secret(variable, prompt):
    value = os.environ.get(variable) or getpass(prompt)
    if not value:
        raise ValueError("La valeur saisie doit être non vide.")
    return value
