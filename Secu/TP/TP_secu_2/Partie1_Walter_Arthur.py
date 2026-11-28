"""TP Blockchain, partie individuelle. L'option --mesure 600 lance le test de Q6."""

import argparse
import hashlib
import json
import math
from time import perf_counter

from ecdsa import BadSignatureError, NIST384p, SigningKey


# Q1. C'est l'intégrité. Si la dépense chez Total passe de 70 € à 700 €,
# l'empreinte recalculée ne correspond plus à celle que garde le bloc suivant.
#
# Q2. Dans main.py, chaque bloc contient les transactions (transaction_list)
# et l'empreinte du bloc précédent (previous_block_hash). Le programme les
# assemble dans block_data, puis calcule l'empreinte SHA-256 de ce texte
# et la stocke dans block_hash. Le premier bloc utilise "0" comme référence.
#
# Q3. Le programme de départ accepte une transaction sans signature et sans
# vérifier si la personne a de quoi payer. Il manque aussi la preuve
# de travail et la vérification de la chaîne. Le carnet reste sur un seul poste.
#
# Q4. La clé privée sert à signer chaque transaction. Avant d'ajouter le bloc,
# le programme vérifie la signature avec la clé publique.
#
# Q5. Le titulaire du carnet peut y inscrire un salaire de 2 000 € même si
# le virement n'a jamais eu lieu. Sa signature ne prouve pas que l'employeur
# a autorisé le paiement.
#
# Q6. On fait varier un compteur appelé nonce et on recalcule l'empreinte
# du bloc à chaque essai. Pendant le test de dix minutes, la meilleure
# empreinte obtenue commençait par six zéros.


def verifier_signature(cle_publique, transaction, signature):
    # Le libellé est encodé en UTF-8 ici aussi, comme au moment de le signer.
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
    limite = perf_counter() + secondes
    essais = 0
    meilleur = -1
    cible = ""
    print(f"Recherche pendant {secondes:g} s…", flush=True)
    while essais == 0 or perf_counter() < limite:
        for nonce in range(essais, essais + 4096):
            valeur = empreinte(prefixe, nonce)
            if valeur.startswith(cible):
                meilleur = len(valeur) - len(valeur.lstrip("0"))
                meilleur_nonce, meilleur_hash = nonce, valeur
                cible = "0" * (meilleur + 1)
        essais += 4096
    print(f"Nombre maximal de zéros en début d'empreinte : {meilleur}.")
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

    # Q4. La même paire de clés sert pour les six écritures du carnet.
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
