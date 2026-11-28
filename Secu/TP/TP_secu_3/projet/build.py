import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

from ca.core import CertificateAuthority
from print_pems import print_pems
from server.core import Server
from tools.core import Configuration
from tools.paths import CA_CERT, CA_KEY, DEFAULT_RESOURCES, PEM_FILES, SERVER_CERT, SERVER_CSR, SERVER_KEY, secret


CA = Configuration("FR", "Bourgogne-Franche-Comté", "Belfort", "Club des Ormes", "Autorité du Club des Ormes")
SERVER = Configuration("FR", "Bourgogne-Franche-Comté", "Belfort", "Club des Ormes", "localhost", ("localhost",))


def build(directory, ca_password, server_password):
    directory.mkdir(parents=True, exist_ok=True)
    if any((directory / name).exists() for name in PEM_FILES):
        raise FileExistsError("Un PEM existe déjà. Choisissez un autre dossier avec --resources.")
    with TemporaryDirectory(dir=directory) as temp:
        stage = Path(temp)
        authority = CertificateAuthority(CA, ca_password, stage / CA_KEY, stage / CA_CERT)
        server = Server(SERVER, server_password, stage / SERVER_KEY, stage / SERVER_CSR)
        authority.sign(server.get_csr(), stage / SERVER_CERT)
        # L’ouverture exclusive préserve le jeu déjà remis, même entre deux lancements.
        created = []
        try:
            for name in PEM_FILES:
                target = directory / name
                with target.open("xb") as output:
                    created.append(target)
                    output.write((stage / name).read_bytes())
        except OSError:
            for target in created:
                target.unlink()
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Générer les cinq PEM du club")
    parser.add_argument("--resources", type=Path, default=DEFAULT_RESOURCES)
    args = parser.parse_args()
    try:
        build(args.resources, secret("TP_CA_MDP", "Mot de passe de la clé CA : "),
              secret("TP_SERVEUR_MDP", "Mot de passe de la clé serveur : "))
        for filename in (CA_CERT, SERVER_CERT):
            print_pems(args.resources / filename)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Génération interrompue : {exc}\n")
