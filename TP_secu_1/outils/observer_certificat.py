"""Relever le certificat TLS public et ses champs cryptographiques.

Complément séparé du programme du TP : pip install -r requirements-certificat.txt
python outils/observer_certificat.py --sortie resultats/certificat_springer.json
La connexion vérifie le nom d'hôte et la chaîne de confiance. Aucun mode insecure.
Le certificat dépend du serveur, de la date et de la négociation du client.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import socket
import ssl
import sys


def analyser_der(der):
    from cryptography import x509
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec, rsa, padding
    cert = x509.load_der_x509_certificate(der)
    cle = cert.public_key()
    if isinstance(cle, rsa.RSAPublicKey):
        algo, taille, exposant = "RSA", cle.key_size, cle.public_numbers().e
    elif isinstance(cle, ec.EllipticCurvePublicKey):
        algo, taille, exposant = "EC " + cle.curve.name, cle.key_size, None
    else:
        algo, taille, exposant = type(cle).__name__, getattr(cle, "key_size", None), None
    param = cert.signature_algorithm_parameters
    if isinstance(param, padding.PKCS1v15):
        bourrage = "RSASSA-PKCS1-v1_5 pour la signature du certificat"
    elif isinstance(param, padding.PSS):
        bourrage = "RSASSA-PSS pour la signature du certificat"
    elif isinstance(param, ec.ECDSA):
        bourrage = "Sans bourrage RSA : signature ECDSA"
    else:
        bourrage = "Non applicable ou non identifié pour cet algorithme"
    try:
        san = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        san = []
    return {"subject": cert.subject.rfc4514_string(), "issuer": cert.issuer.rfc4514_string(),
            "san_dns": san, "serial_hex": hex(cert.serial_number),
            "not_before_utc": cert.not_valid_before_utc.isoformat(),
            "not_after_utc": cert.not_valid_after_utc.isoformat(),
            "cle_publique_algorithme": algo, "cle_publique_bits": taille,
            "exposant_public_rsa": exposant,
            "signature_certificat_oid": cert.signature_algorithm_oid.dotted_string,
            "signature_certificat_nom": cert.signature_algorithm_oid._name,
            "empreinte_utilisee_dans_signature": cert.signature_hash_algorithm.name if cert.signature_hash_algorithm else None,
            "bourrage_signature_certificat": bourrage,
            "empreinte_certificat_sha256": cert.fingerprint(hashes.SHA256()).hex(),
            "note": "La signature du certificat utilise la clé de l'autorité émettrice ; elle n'indique pas un chiffrement RSA du trafic TLS."}


def observer(hote, sortie):
    resultat = {"hote": hote, "port": 443,
                "observation_utc": datetime.now(timezone.utc).isoformat(),
                "python": platform.python_version(), "openssl": ssl.OPENSSL_VERSION}
    try:
        contexte = ssl.create_default_context()
        with socket.create_connection((hote, 443), timeout=20) as sock:
            with contexte.wrap_socket(sock, server_hostname=hote) as tls:
                der = tls.getpeercert(binary_form=True)
                resultat.update({"tls": tls.version(), "suite_tls": tls.cipher(),
                                 "validation_tls": True, **analyser_der(der), "statut": "observe"})
        pem = ssl.DER_cert_to_PEM_cert(der)
        sortie.with_suffix(".pem").write_text(pem, encoding="ascii")
    except (OSError, ValueError, ImportError) as erreur:
        resultat.update({"statut": "echec", "erreur_type": type(erreur).__name__, "erreur": str(erreur)})
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("CERTIFICAT_JSON=" + json.dumps(resultat, ensure_ascii=False))
    return 0 if resultat["statut"] == "observe" else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--hote", default="link.springer.com")
    parser.add_argument("--sortie", type=Path, default=Path("resultats/certificat_springer.json"))
    args = parser.parse_args()
    args.sortie.parent.mkdir(parents=True, exist_ok=True)
    return observer(args.hote, args.sortie)


if __name__ == "__main__":
    sys.exit(main())
