"""Pilote des tests du .bat ; fonctionne aussi sous Linux pour la CI.

Exécute chaque étape dans un processus séparé, contrôle les codes de retour
et vérifie les JSON produits. Un échec fait échouer le bilan global.
Par défaut, le certificat archivé est vérifié hors ligne. --certificat ajoute
une observation réseau distincte sans écraser la preuve citée dans le rapport.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import ssl
import subprocess
import sys
import zipfile

RACINE = Path(__file__).resolve().parents[1]
SORTIE = RACINE / "resultats/tests_windows"


def executer(nom, arguments, code_attendu=0):
    print(f"\n=== {nom} ===", flush=True)
    environnement = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    resultat = subprocess.run([sys.executable, *arguments], cwd=RACINE,
                              env=environnement, capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
    journal = resultat.stdout + resultat.stderr
    print(journal, flush=True)
    (SORTIE / f"{nom}.log").write_text(journal, encoding="utf-8")
    if resultat.returncode != code_attendu:
        raise RuntimeError(f"Code retour {resultat.returncode}, attendu {code_attendu}.")


def verifier_simulation(nom, partie, message):
    chemin = SORTIE / f"{nom}.json"
    executer(nom, ["Walter_Arthur_main.py", "--partie", partie,
                   "--message", message, "--sortie", str(chemin)])
    donnees = json.loads(chemin.read_text(encoding="utf-8"))
    for cle in ["partie1", "partie3"]:
        if cle in donnees:
            resultat = donnees[cle]
            if resultat["message_retrouve"] != message or not resultat["signature_valide"]:
                raise RuntimeError("Le texte ou la signature ne correspond pas.")
    if "partie2" in donnees:
        resultat = donnees["partie2"]
        if resultat["crt_exemple_tp"]["m"] != 513:
            raise RuntimeError("Exemple CRT incorrect.")
        if resultat["dechiffrement_alice_crt"] != resultat["dechiffrement_alice_direct"]:
            raise RuntimeError("Désaccord entre CRT et calcul direct.")


def verifier_certificat_archive():
    # Ce contrôle porte sur l'observation datée du rapport, pas sur le serveur actuel.
    from observer_certificat import analyser_der
    dossier = RACINE / "resultats"
    releve = json.loads((dossier / "certificat_springer.json").read_text(encoding="utf-8"))
    der = ssl.PEM_cert_to_DER_cert((dossier / "certificat_springer.pem").read_text(encoding="ascii"))
    champs = analyser_der(der)
    if releve["statut"] != "observe" or not releve["validation_tls"]:
        raise RuntimeError("Le relevé archivé ne décrit pas une observation TLS validée.")
    if any(releve.get(cle) != valeur for cle, valeur in champs.items()):
        raise RuntimeError("Le certificat PEM ne correspond pas au JSON du rapport.")
    print("Certificat archivé : tous les champs correspondent au PEM.")


def verifier_documents():
    # Vérification d'intégrité du paquet ; la mise en page est contrôlée à l'édition.
    pdf = RACINE / "docs/Walter_Arthur.pdf"
    if not pdf.read_bytes().startswith(b"%PDF-"):
        raise RuntimeError("Le rapport PDF est absent ou invalide.")
    with zipfile.ZipFile(RACINE / "docs/Walter_Arthur.docx") as archive:
        if archive.testzip() is not None or "word/document.xml" not in archive.namelist():
            raise RuntimeError("Le rapport Word est invalide.")
    print("Rapports PDF et Word présents et lisibles comme fichiers.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificat", action="store_true", help="Ajouter une observation TLS actuelle")
    args = parser.parse_args()
    SORTIE.mkdir(parents=True, exist_ok=True)
    etapes = [
        ("tests_rsa", lambda: executer("tests_rsa", ["-m", "unittest", "discover", "-s", "tests", "-v"])),
        ("tests_x509", lambda: executer("tests_x509", ["outils/test_certificat.py"])),
        ("certificat_archive", verifier_certificat_archive),
        ("demonstration_complete", lambda: verifier_simulation("demonstration_complete", "toutes", "Bonjour Alice")),
        ("message_long", lambda: verifier_simulation("message_long", "3", "Un message long avec des accents é et un emoji 😀. " * 4)),
        ("message_vide", lambda: verifier_simulation("message_vide", "3", "")),
        ("limite_partie1", lambda: executer("limite_partie1", ["Walter_Arthur_main.py", "--partie", "1", "--message", "A" * 26], 2)),
        ("rapports", verifier_documents),
    ]
    if args.certificat:
        etapes.append(("certificat_actuel", lambda: executer("certificat_actuel", ["outils/observer_certificat.py", "--sortie", str(SORTIE / "certificat_actuel.json")])))
    bilan = []
    for nom, fonction in etapes:
        capture = io.StringIO()
        try:
            # Le log complet comprend aussi les exceptions des contrôles internes.
            with contextlib.redirect_stdout(capture):
                fonction()
            bilan.append({"etape": nom, "succes": True})
        except Exception as erreur:
            capture.write(f"ECHEC {nom} : {type(erreur).__name__} : {erreur}\n")
            bilan.append({"etape": nom, "succes": False, "erreur": str(erreur)})
        print(capture.getvalue(), flush=True)
        (SORTIE / f"{nom}.log").write_text(capture.getvalue(), encoding="utf-8")
    (SORTIE / "bilan.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Bilan : {sum(e['succes'] for e in bilan)}/{len(bilan)} étapes réussies.")
    print(f"Journaux : {SORTIE}")
    return 0 if all(e["succes"] for e in bilan) else 1


if __name__ == "__main__":
    sys.exit(main())
