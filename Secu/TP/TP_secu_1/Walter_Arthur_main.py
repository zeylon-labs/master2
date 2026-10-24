# -*- coding: utf-8 -*-
"""Démonstrations du TP RSA, avec Python 3.10 ou plus récent.

python Walter_Arthur_main.py --partie 1 --message "Bonjour Alice"
python Walter_Arthur_main.py --partie 2
python Walter_Arthur_main.py --partie 3 --message "Un message beaucoup plus long..."
python Walter_Arthur_main.py --partie toutes --message "Bonjour Alice"

L'option toutes enchaîne les trois parties. Sans --message, le programme
demande le texte à saisir, sauf pour la partie 2 qui utilise ses propres exemples.
"""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import sys

import Walter_Arthur_util as rsa

# Les calculs sont regroupés dans Walter_Arthur_util.py.


def partie1(message):
    """Chiffrer pour Alice, puis vérifier la signature de Bob à la réception."""
    paquet = rsa.home_envoyer(message)
    texte, valide = rsa.home_recevoir(paquet)
    return {"message": message, "octets_utf8": len(message.encode("utf-8")),
            "module_alice_bits": rsa.na.bit_length(), "module_bob_bits": rsa.nb.bit_length(),
            "limite_octets": rsa.LIMITE_MESSAGE, "chiffre": paquet.chiffre,
            "sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
            "tailles_blocs_hash": [len(b) for b in rsa.home_blocs_hash(message)],
            "signatures": paquet.signatures, "message_retrouve": texte,
            "signature_valide": valide}


def partie2():
    """Compter les opérations et comparer le calcul direct au CRT."""
    exemple = rsa.home_preparer_crt(137, 131, 11787)
    trace = rsa.home_mod_expnoent_trace(3, 13, 17)
    chiffre = rsa.home_mod_expnoent(513, rsa.ea, rsa.na)
    traces_messages = []
    for message in [1, 42, 513, 123456789]:
        # On change le message, mais pas la clé : le nombre de bits à 1
        # de l'exposant privé reste donc le même.
        chiffre_message = rsa.home_mod_expnoent(message, rsa.ea, rsa.na)
        trace_message = rsa.home_mod_expnoent_trace(chiffre_message, rsa.da, rsa.na)
        traces_messages.append({"message": message, "resultat": trace_message.resultat,
                                "conditionnelles": trace_message.multiplications_conditionnelles,
                                "carres": trace_message.carres})
    return {"trace_exemple": asdict(trace), "ordre_bits": "poids faible vers poids fort",
            "crt_exemple_tp": {**asdict(exemple), "c": 8363,
                                      "mp": rsa.home_mod_expnoent(8363, exemple.dp, exemple.p),
                                      "mq": rsa.home_mod_expnoent(8363, exemple.dq, exemple.q),
                                      "m": rsa.home_rsa_crt(8363, exemple)},
            "dechiffrement_alice_direct": rsa.home_mod_expnoent(chiffre, rsa.da, rsa.na),
            "dechiffrement_alice_crt": rsa.home_rsa_crt(chiffre, rsa.CRT_ALICE),
            "traces_messages": traces_messages,
            "temps_bonus": rsa.home_comparer_temps([1, 42, 513, 123456789])}


def partie3(message):
    """Découper un texte, le chiffrer avec bourrage et retrouver le message."""
    paquet = rsa.home_envoyer_blocs(message)
    texte, valide = rsa.home_recevoir_blocs(paquet)
    # Le calcul direct doit retrouver le même texte que le CRT.
    reception_directe = rsa.home_recevoir_blocs(paquet, utiliser_crt=False)
    assert reception_directe == (texte, valide)
    return {"message": message, "octets_utf8": len(message.encode("utf-8")),
            "k_octets": rsa.K_BLOC, "j_max_octets": rsa.J_MESSAGE,
            "ps_min_avec_j_max": rsa.K_BLOC - rsa.J_MESSAGE - 3,
            "nombre_blocs": len(paquet.chiffres), "chiffres": paquet.chiffres,
            "message_retrouve": texte, "signature_valide": valide,
            "crt_identique_au_direct": True,
            "note": "Bourrage aléatoire : les chiffres varient entre deux exécutions."}


def main():
    """Choisir la partie à lancer et afficher les résultats dans le terminal."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partie", choices=["1", "2", "3", "toutes"], default="toutes",
                        help="1 : échange RSA ; 2 : traces et CRT ; 3 : bourrage ; toutes : les trois parties")
    parser.add_argument("--message", help="Partie 1 limitée à 25 octets UTF-8")
    parser.add_argument("--sortie", type=Path, help="Enregistrer aussi les résultats JSON")
    args = parser.parse_args()
    if args.message is not None:
        message = args.message
    elif args.partie == "2":
        message = ""
    else:
        message = input("Message de Bob : ")
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
    # Le JSON permet de lire les valeurs calculées et de les enregistrer si besoin.
    print(sortie)
    if args.sortie:
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        args.sortie.write_text(sortie + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
