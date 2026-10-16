# -*- coding: utf-8 -*-
"""TP RSA de M. ABBAS-TURKI - trois parties pédagogiques, Python 3.10+.

python Walter_Arthur_main.py --partie toutes --message "Bonjour Alice"
python Walter_Arthur_main.py --partie 3 --message "Un message beaucoup plus long..."
python Walter_Arthur_main.py --test
Le code utilise de petites clés et des signatures RSA non standard, sans PSS.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import sys
import unittest

import Walter_Arthur_util as u


def partie1(message):
    paquet = u.home_envoyer(message)
    texte, valide = u.home_recevoir(paquet)
    return {"message": message, "octets_utf8": len(message.encode("utf-8")),
            "module_alice_bits": u.na.bit_length(), "module_bob_bits": u.nb.bit_length(),
            "limite_octets": u.LIMITE_MESSAGE, "chiffre": paquet.chiffre,
            "sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
            "tailles_blocs_hash": [len(b) for b in u.home_blocs_hash(message)],
            "signatures": paquet.signatures, "message_retrouve": texte,
            "signature_valide": valide}


def partie2():
    exemple = u.home_preparer_crt(137, 131, 11787)
    trace = u.home_mod_expnoent_trace(3, 13, 17)
    c = u.home_mod_expnoent(513, u.ea, u.na)
    traces_messages = []
    for m in [1, 42, 513, 123456789]:
        t = u.home_mod_expnoent_trace(u.home_mod_expnoent(m, u.ea, u.na), u.da, u.na)
        traces_messages.append({"message": m, "resultat": t.resultat,
                                "conditionnelles": t.multiplications_conditionnelles,
                                "carres": t.carres})
    return {"trace_exemple": asdict(trace), "ordre_bits": "poids faible vers poids fort",
            "crt_exemple_professeur": {**asdict(exemple), "c": 8363,
                                      "mp": u.home_mod_expnoent(8363, exemple.dp, exemple.p),
                                      "mq": u.home_mod_expnoent(8363, exemple.dq, exemple.q),
                                      "m": u.home_rsa_crt(8363, exemple)},
            "dechiffrement_alice_direct": u.home_mod_expnoent(c, u.da, u.na),
            "dechiffrement_alice_crt": u.home_rsa_crt(c, u.CRT_ALICE),
            "traces_messages": traces_messages,
            "temps_bonus": u.home_comparer_temps([1, 42, 513, 123456789])}


def partie3(message):
    paquet = u.home_envoyer_blocs(message)
    texte, valide = u.home_recevoir_blocs(paquet)
    direct = u.home_recevoir_blocs(paquet, utiliser_crt=False)
    assert direct == (texte, valide)
    return {"message": message, "octets_utf8": len(message.encode("utf-8")),
            "k_octets": u.K_BLOC, "j_max_octets": u.J_MESSAGE,
            "ps_min_avec_j_max": u.K_BLOC - u.J_MESSAGE - 3,
            "nombre_blocs": len(paquet.chiffres), "chiffres": paquet.chiffres,
            "message_retrouve": texte, "signature_valide": valide,
            "crt_identique_au_direct": True,
            "note": "Bourrage aléatoire : les chiffres varient entre deux exécutions."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partie", choices=["1", "2", "3", "toutes"], default="toutes")
    parser.add_argument("--message", help="Partie 1 limitée à 25 octets UTF-8")
    parser.add_argument("--sortie", type=Path, help="Enregistrer aussi les résultats JSON")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        dossier_tests = Path(__file__).parent / "tests"
        if not dossier_tests.is_dir():
            parser.error("Conserver le dossier tests pour exécuter --test.")
        suite = unittest.defaultTestLoader.discover(str(dossier_tests))
        resultat = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if resultat.wasSuccessful() else 1
    message = args.message if args.message is not None else ("" if args.partie == "2" else input("Message de Bob : "))
    resultats = {"environnement": {"python": platform.python_version(),
                                  "systeme": platform.platform()}}
    try:
        if args.partie in ("1", "toutes"):
            resultats["partie1"] = partie1(message)
        if args.partie in ("2", "toutes"):
            resultats["partie2"] = partie2()
        if args.partie in ("3", "toutes"):
            resultats["partie3"] = partie3(message)
    except ValueError as erreur:
        parser.error(str(erreur))
    sortie = json.dumps(resultats, ensure_ascii=False, indent=2)
    print(sortie)
    if args.sortie:
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        args.sortie.write_text(sortie + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
