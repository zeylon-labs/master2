"""TP Blockchain, partie individuelle. L'option --mesure 600 lance le test de Q6."""

import argparse
import hashlib
import json
import math
from time import perf_counter

from ecdsa import BadSignatureError, NIST384p, SigningKey


# Q1. Le critère prioritaire est l'intégrité. Si le montant d'une dépense
# change, son empreinte change aussi et le bloc suivant référence encore
# l'ancienne empreinte. Le rapprochement des deux révèle l'incohérence.
# Les opérations de cet exemple sont lisibles en clair.
#
# Q2. Dans main.py, chaque Block contient previous_block_hash et
# transaction_list. block_data assemble les libellés avec « - », puis ajoute
# l'empreinte précédente. block_hash est le SHA-256 de ce texte encodé en
# UTF-8, écrit en hexadécimal. Le premier bloc contient « Genesis Block » et
# utilise la chaîne « 0 » comme référence. Les six opérations viennent ensuite.
#
# Q3. Le programme de départ relie les blocs, mais chacun peut y inscrire un
# libellé. Il manque la signature et sa vérification, le contrôle des fonds
# de l'émetteur et la preuve de travail. Le programme affiche les empreintes
# déjà stockées sans les recalculer pour contrôler la chaîne. Il conserve
# aussi une seule copie locale, sans les autres mineurs décrits dans le sujet.
#
# Q5. Si j'inscris « L'employeur me verse 2000 € », ma signature prouve que
# j'ai approuvé cette écriture. Rien ne prouve que mon employeur a ordonné
# le virement, ni que l'argent est arrivé sur mon compte. Je peux donc tenir
# un registre cohérent dans lequel mon solde de départ est faux.
#
# Q6. Un zéro hexadécimal représente quatre bits. Pour d zéros imposés,
# la probabilité de succès par essai vaut 1/16**d, soit 16**d essais en
# moyenne. À débit égal, un zéro de plus multiplie le travail moyen par 16.
# Le meilleur résultat en dix minutes dépend du bloc, du PC et de la chance.
# Sur le Core i5-12400F, le meilleur résultat de la mesure est de 6 zéros.
# Le nonce 26 361 962 a été trouvé après 59,06 s. Au terme des 600,01 s,
# 298 602 496 nonces avaient été testés, sans trouver de septième zéro.
# Empreinte : 000000ce3ec1c6b558fb64d2137f8fab837e2135c241f7f628126c20f3f6983e


def verifier_signature(cle_publique, transaction, signature):
    # Q4. La vérification porte sur les mêmes octets que la signature.
    try:
        return cle_publique.verify(
            signature, transaction.encode("utf-8"), hashfunc=hashlib.sha256
        )
    except BadSignatureError:
        return False


class Block:
    def __init__(self, previous_block_hash, transaction_list, signatures, difficulte):
        self.previous_block_hash = previous_block_hash
        self.transaction_list = list(transaction_list)
        self.signatures = list(signatures)
        self.block_data = f"{' - '.join(transaction_list)} - {previous_block_hash}"
        # Q6. Seul le nonce change entre deux essais sur ce bloc.
        prefixe = self.prefixe_minage()
        cible = "0" * difficulte
        self.nonce = 0
        while True:
            self.block_hash = empreinte(prefixe, self.nonce)
            if self.block_hash.startswith(cible):
                break
            self.nonce += 1

    def prefixe_minage(self):
        champs = [self.previous_block_hash, self.transaction_list,
                  [sig.hex() for sig in self.signatures]]
        return json.dumps(champs, separators=(",", ":"), ensure_ascii=False).encode("utf-8") + b"|"


def empreinte(prefixe, nonce):
    return hashlib.sha256(prefixe + str(nonce).encode("ascii")).hexdigest()


class Blockchain:
    def __init__(self, cle_publique, difficulte=2):
        if not 1 <= difficulte <= 64:
            raise ValueError("La difficulté doit être comprise entre 1 et 64.")
        self.chain = []
        self.cle_publique = cle_publique
        self.difficulte = difficulte
        self.generate_genesis_block()

    def generate_genesis_block(self):
        self.chain.append(Block("0", ["Genesis Block"], [], self.difficulte))

    def create_block_from_transaction(self, transaction_list, signatures):
        # Un justificatif signé est nécessaire pour chaque ligne du bloc.
        if not transaction_list or len(signatures) != len(transaction_list):
            raise ValueError("Il faut une signature par transaction.")
        for transaction, signature in zip(transaction_list, signatures):
            if not verifier_signature(self.cle_publique, transaction, signature):
                raise ValueError("La signature de la transaction est incorrecte.")
        self.chain.append(Block(self.last_block.block_hash, transaction_list,
                                signatures, self.difficulte))

    def display_chain(self):
        for i, bloc in enumerate(self.chain, start=1):
            print(f"Data {i}: {bloc.block_data}")
            print(f"Hash {i}: {bloc.block_hash} (nonce {bloc.nonce})")

    @property
    def last_block(self):
        return self.chain[-1]


def mesurer_minage(bloc, secondes):
    if not math.isfinite(secondes) or secondes <= 0:
        raise ValueError("La durée de mesure doit être positive et finie.")
    prefixe = bloc.prefixe_minage()
    debut = perf_counter()
    limite = debut + secondes
    essais = 0
    meilleur = -1
    cible = ""
    while essais == 0 or perf_counter() < limite:
        # On consulte l'horloge par séries pour mesurer surtout le hachage.
        for nonce in range(essais, essais + 4096):
            valeur = empreinte(prefixe, nonce)
            if valeur.startswith(cible):
                meilleur = len(valeur) - len(valeur.lstrip("0"))
                meilleur_nonce, meilleur_hash = nonce, valeur
                cible = "0" * (meilleur + 1)
                print(f"{meilleur} zéro(s) en {perf_counter() - debut:.2f} s "
                      f"(nonce {nonce})", flush=True)
        essais += 4096
    duree = perf_counter() - debut
    print(f"Mesure : {essais} essais en {duree:.2f} s ({essais / duree:.0f} essais/s).")
    print(f"Meilleure preuve : {meilleur} zéros, nonce {meilleur_nonce}, SHA-256 {meilleur_hash}")
    return meilleur, meilleur_nonce, meilleur_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mesure", type=float, metavar="SECONDES",
                        help="chronométrer la recherche sur le premier bloc signé")
    args = parser.parse_args()
    if args.mesure is not None and (not math.isfinite(args.mesure) or args.mesure <= 0):
        parser.error("--mesure attend une durée positive et finie")

    t1 = "L'employeur me verse 2000 €"
    t2 = "J'ai dépensé 70 € chez Total"
    t3 = "J'ai dépensé 5 € chez amazone"
    t4 = "J'ai dépensé 100 € chez Auchan"
    t5 = "J'ai dépensé 110 € chez Engi"
    t6 = "J'ai dépensé 30 € chez SFR"

    # Q4. Une paire pour la tenue de mon carnet. La clé privée reste ici.
    cle_privee = SigningKey.generate(curve=NIST384p)
    cle_publique = cle_privee.verifying_key
    myblockchain = Blockchain(cle_publique)
    for transaction in (t1, t2, t3, t4, t5, t6):
        signature = cle_privee.sign_deterministic(transaction.encode("utf-8"),
                                                  hashfunc=hashlib.sha256)
        myblockchain.create_block_from_transaction([transaction], [signature])
    myblockchain.display_chain()

    preuve = myblockchain.chain[2].signatures[0]
    print("Signature de la dépense de 70 € valide :", verifier_signature(cle_publique, t2, preuve))
    print("Même signature avec 700 € :", verifier_signature(cle_publique, t2.replace("70", "700"), preuve))
    if args.mesure is not None:
        mesurer_minage(myblockchain.chain[1], args.mesure)


if __name__ == "__main__":
    main()
