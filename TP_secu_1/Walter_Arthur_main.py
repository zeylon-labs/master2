# -*- coding: utf-8 -*-
"""TP RSA - chiffrement, signature, traces et bourrage. Python 3.10+.

python Walter_Arthur_main.py --partie toutes --message "Bonjour Alice"
python Walter_Arthur_main.py --partie 3 --message "Un message beaucoup plus long..."
python Walter_Arthur_main.py --test
Les petites clés servent aux calculs du TP. La signature en deux blocs
est une adaptation pour ces clés ; ce n'est pas une signature RSA-PSS.
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

# Ce fichier lance les trois parties et affiche ce qu'elles donnent.
# Les fonctions de calcul sont regroupées dans Walter_Arthur_util.py.
# On l'importe sous le nom u pour écrire, par exemple, u.home_envoyer(...).


def partie1(message):
    """Faire l'aller-retour du message entre Bob et Alice.

    Bob prépare le message chiffré et les signatures. Alice reçoit cet envoi,
    retrouve le texte et vérifie les signatures. On regroupe ensuite les
    valeurs pour pouvoir lire chaque résultat dans la console.
    """
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
    """Observer les opérations, puis comparer les deux déchiffrements.

    Les nombres 137, 131, 11787 et 8363 reprennent l'exemple CRT du TP.
    Le petit calcul 3**13 modulo 17 permet de suivre facilement les bits.
    asdict rassemble les champs d'un résultat pour les afficher en JSON.
    """
    exemple = u.home_preparer_crt(137, 131, 11787)
    trace = u.home_mod_expnoent_trace(3, 13, 17)
    c = u.home_mod_expnoent(513, u.ea, u.na)
    traces_messages = []
    for m in [1, 42, 513, 123456789]:
        # On change le message, mais pas la clé : le nombre de bits à 1
        # de l'exposant privé reste donc le même.
        t = u.home_mod_expnoent_trace(u.home_mod_expnoent(m, u.ea, u.na), u.da, u.na)
        traces_messages.append({"message": m, "resultat": t.resultat,
                                "conditionnelles": t.multiplications_conditionnelles,
                                "carres": t.carres})
    return {"trace_exemple": asdict(trace), "ordre_bits": "poids faible vers poids fort",
            "crt_exemple_tp": {**asdict(exemple), "c": 8363,
                                      "mp": u.home_mod_expnoent(8363, exemple.dp, exemple.p),
                                      "mq": u.home_mod_expnoent(8363, exemple.dq, exemple.q),
                                      "m": u.home_rsa_crt(8363, exemple)},
            "dechiffrement_alice_direct": u.home_mod_expnoent(c, u.da, u.na),
            "dechiffrement_alice_crt": u.home_rsa_crt(c, u.CRT_ALICE),
            "traces_messages": traces_messages,
            "temps_bonus": u.home_comparer_temps([1, 42, 513, 123456789])}


def partie3(message):
    """Envoyer un texte qui peut occuper plusieurs blocs.

    Le bourrage contient un aléa : les chiffrés peuvent changer d'un envoi
    à l'autre. Alice doit pourtant retrouver exactement le même texte.
    Le calcul direct sert ici à vérifier le résultat obtenu par le CRT.
    """
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
    """Lire la commande et lancer la partie demandée.

    Sans --message, le texte est demandé dans le terminal, sauf en partie 2.
    --test lance les vérifications ; --sortie garde aussi une copie des
    résultats dans un fichier. Le .bat lit le code de retour pour savoir
    si l'exécution s'est bien passée.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--partie", choices=["1", "2", "3", "toutes"], default="toutes")
    parser.add_argument("--message", help="Partie 1 limitée à 25 octets UTF-8")
    parser.add_argument("--sortie", type=Path, help="Enregistrer aussi les résultats JSON")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()
    if args.test:
        # Charger les tests du dossier tests, puis afficher les réussites
        # et les erreurs. Sans ce dossier, on signale le problème.
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
    # Garder les accents tels quels et indenter le texte pour faciliter la lecture.
    print(sortie)
    if args.sortie:
        args.sortie.parent.mkdir(parents=True, exist_ok=True)
        args.sortie.write_text(sortie + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    # Démarrer le programme quand on lance ce fichier dans le terminal.
    sys.exit(main())
