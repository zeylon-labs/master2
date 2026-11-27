"""Comptes entre trois amis. Lancer avec --menu pour saisir des opérations."""

import argparse
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone

from ecdsa import BadSignatureError, NIST384p, SigningKey


AMIS = ("Alice", "Benoît", "Chloé")
DIFFICULTE = 2


def encoder(donnees):
    return json.dumps(donnees, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":")).encode("utf-8")


def euros(centimes):
    montant = abs(centimes)
    return f"{montant // 100},{montant % 100:02d} €"


def lire_montant(texte):
    if not re.fullmatch(r"[0-9]+([.,][0-9]{1,2})?", texte.strip()):
        raise ValueError("Saisir un montant en euros, par exemple 12,50.")
    entier, _, fraction = texte.strip().replace(",", ".").partition(".")
    montant = 100 * int(entier) + int(fraction.ljust(2, "0"))
    if montant == 0:
        raise ValueError("Le montant doit être positif.")
    return montant


@dataclass(frozen=True)
class Transaction:
    date: str
    nature: str
    payeur: str
    beneficiaires: tuple
    centimes: int
    motif: str

    def participants(self):
        return set(self.beneficiaires) | {self.payeur}

    def verifier(self):
        if self.nature not in ("avance", "achat", "remboursement"):
            raise ValueError("Type d'opération inconnu.")
        if type(self.centimes) is not int or self.centimes <= 0:
            raise ValueError("Le montant doit être positif, en centimes entiers.")
        if not self.motif.strip():
            raise ValueError("Préciser le motif de l'opération.")
        if datetime.fromisoformat(self.date).utcoffset() is None:
            raise ValueError("La date doit inclure le fuseau horaire.")
        groupe = set(self.beneficiaires)
        if not self.participants().issubset(AMIS) or len(groupe) != len(self.beneficiaires):
            raise ValueError("Nom inconnu ou bénéficiaire en double.")
        if self.nature == "achat":
            if self.payeur not in groupe or len(groupe) < 2:
                raise ValueError("Un achat se partage entre le payeur et au moins un autre ami.")
        elif len(groupe) != 1 or self.payeur in groupe:
            raise ValueError("Choisir un seul autre ami pour cette opération.")

    def message(self, precedent):
        # L'accord porte aussi sur la place de cette écriture dans le carnet.
        return encoder([precedent, asdict(self)])

    def parts(self):
        quotient, reste = divmod(self.centimes, len(self.beneficiaires))
        # Chaque centime restant revient à un bénéficiaire, par ordre alphabétique.
        return {ami: quotient + (i < reste)
                for i, ami in enumerate(sorted(self.beneficiaires))}

    def libelle(self):
        personnes = ", ".join(self.beneficiaires)
        montant = euros(self.centimes)
        if self.nature == "avance":
            detail = f"{self.payeur} avance {montant} à {personnes}"
        elif self.nature == "remboursement":
            detail = f"{self.payeur} rembourse {montant} à {personnes}"
        else:
            detail = f"{self.payeur} règle {montant} pour le groupe ({personnes})"
        return f"{self.date} | {detail} | {self.motif}"


def verifier_accords(operation, precedent, signatures, cles_publiques):
    if set(signatures) != operation.participants():
        raise ValueError("Il faut exactement les signatures des personnes concernées.")
    message = operation.message(precedent)
    for ami, signature in signatures.items():
        try:
            cles_publiques[ami].verify(bytes.fromhex(signature), message,
                                       hashfunc=hashlib.sha256)
        except (BadSignatureError, ValueError, TypeError) as erreur:
            raise ValueError(f"Signature incorrecte pour {ami}.") from erreur


@dataclass
class Bloc:
    precedent: str
    operation: Transaction | None
    signatures: dict
    nonce: int = 0
    empreinte: str = ""

    def prefixe(self):
        operation = asdict(self.operation) if self.operation is not None else None
        return encoder([self.precedent, operation, self.signatures]) + b"|"

    def miner(self):
        prefixe = self.prefixe()
        while True:
            self.empreinte = self.hacher(prefixe)
            if self.empreinte.startswith("0" * DIFFICULTE):
                return
            self.nonce += 1

    def hacher(self, prefixe):
        return hashlib.sha256(prefixe + str(self.nonce).encode("ascii")).hexdigest()


def enregistrer_soldes(soldes, operation):
    # soldes[A][B] > 0 signifie que B doit de l'argent à A.
    payeur = operation.payeur
    if operation.nature == "remboursement":
        creancier = operation.beneficiaires[0]
        if operation.centimes > soldes[creancier][payeur]:
            raise ValueError(f"Le remboursement dépasse la dette de {payeur} envers {creancier}.")
    for ami, part in operation.parts().items():
        if ami != payeur:
            soldes[payeur][ami] += part
            soldes[ami][payeur] -= part


class Blockchain:
    def __init__(self, cles_publiques):
        if set(cles_publiques) != set(AMIS):
            raise ValueError("Il faut une clé publique par ami.")
        if len({cle.to_string() for cle in cles_publiques.values()}) != len(AMIS):
            raise ValueError("Chaque ami doit avoir sa propre clé.")
        self.cles_publiques = dict(cles_publiques)
        genese = Bloc("0", None, {})
        genese.miner()
        self.blocs = [genese]
        self.empreinte_genese = genese.empreinte

    @property
    def derniere_empreinte(self):
        return self.blocs[-1].empreinte

    def ajouter(self, operation, signatures):
        soldes = self.valider()
        operation.verifier()
        precedent = self.derniere_empreinte
        verifier_accords(operation, precedent, signatures, self.cles_publiques)
        enregistrer_soldes(soldes, operation)
        bloc = Bloc(precedent, operation, signatures.copy())
        bloc.miner()
        self.blocs.append(bloc)

    def valider(self):
        soldes = {ami: {autre: 0 for autre in AMIS if autre != ami} for ami in AMIS}
        if not self.blocs or self.blocs[0].empreinte != self.empreinte_genese:
            raise ValueError("Le bloc de genèse est absent ou a changé.")
        precedent = "0"
        for i, bloc in enumerate(self.blocs):
            try:
                if bloc.precedent != precedent:
                    raise ValueError("Lien avec le bloc précédent incorrect.")
                if type(bloc.nonce) is not int or bloc.nonce < 0:
                    raise ValueError("Nonce invalide.")
                if bloc.hacher(bloc.prefixe()) != bloc.empreinte:
                    raise ValueError("Empreinte différente du contenu.")
                if not bloc.empreinte.startswith("0" * DIFFICULTE):
                    raise ValueError("Preuve de travail insuffisante.")
                if i > 0:
                    if bloc.operation is None:
                        raise ValueError("Opération manquante.")
                    bloc.operation.verifier()
                    verifier_accords(bloc.operation, precedent, bloc.signatures, self.cles_publiques)
                    enregistrer_soldes(soldes, bloc.operation)
            except ValueError as erreur:
                raise ValueError(f"Bloc {i} : {erreur}") from erreur
            precedent = bloc.empreinte
        return soldes

    def historique(self, ami):
        self.valider()
        return [bloc.operation for bloc in self.blocs[1:] if ami in bloc.operation.participants()]


def afficher_soldes(chaine, ami):
    for autre, solde in chaine.valider()[ami].items():
        if solde > 0:
            print(f"{autre} doit {euros(solde)} à {ami}.")
        elif solde < 0:
            print(f"{ami} doit {euros(solde)} à {autre}.")
        else:
            print(f"{ami} et {autre} sont quittes.")


def afficher_historique(chaine, ami):
    operations = chaine.historique(ami)
    print(f"Historique pour {ami}")
    if not operations:
        print("Aucune opération.")
    for operation in operations:
        print(operation.libelle())


def proposer(chaine, operation, cles_privees, accepter):
    operation.verifier()
    print(operation.libelle())
    signatures = {}
    precedent = chaine.derniere_empreinte
    for ami in sorted(operation.participants()):
        if not accepter(ami):
            print(f"{ami} refuse. L'opération est annulée.")
            return False
        signatures[ami] = cles_privees[ami].sign_deterministic(
            operation.message(precedent), hashfunc=hashlib.sha256
        ).hex()
    chaine.ajouter(operation, signatures)
    print(f"Bloc {len(chaine.blocs) - 1} ajouté. Signatures : {', '.join(signatures)}.")
    return True


def choisir_amis(invite, multiple=False):
    print(" / ".join(f"{i} = {ami}" for i, ami in enumerate(AMIS, 1)))
    saisie = input(invite).split(",")
    if (not multiple and len(saisie) != 1) or any(s.strip() not in ("1", "2", "3") for s in saisie):
        raise ValueError("Choisir un numéro par personne parmi 1, 2 et 3.")
    return tuple(AMIS[int(s) - 1] for s in saisie)


def menu(chaine, cles):
    while True:
        print("\n1 Opération   2 Vérifier la chaîne   3 Soldes   4 Historique   0 Quitter")
        choix = input("> ").strip()
        try:
            if choix == "0":
                return
            if choix == "1":
                nature = input("avance / achat / remboursement : ").strip().lower()
                payeur = choisir_amis("Qui paie ? ")[0]
                if nature == "achat":
                    beneficiaires = choisir_amis("Qui partage l'achat (payeur compris, ex. 1,2,3) ? ", True)
                else:
                    beneficiaires = choisir_amis("Qui reçoit l'argent ? ")
                montant = lire_montant(input("Montant total en euros : "))
                motif = input("Motif : ").strip()
                operation = Transaction(datetime.now(timezone.utc).isoformat(timespec="seconds"),
                                        nature, payeur, beneficiaires, montant, motif)
                proposer(chaine, operation, cles,
                         lambda ami: input(f"{ami}, valides-tu ? [o/N] ").strip().lower() in ("o", "oui"))
            elif choix == "2":
                chaine.valider()
                print(f"Chaîne valide. Opérations enregistrées : {len(chaine.blocs) - 1}.")
            elif choix in ("3", "4"):
                ami = choisir_amis("Pour quel ami ? ")[0]
                if choix == "3":
                    afficher_soldes(chaine, ami)
                else:
                    afficher_historique(chaine, ami)
            else:
                print("Choisir une option du menu.")
        except ValueError as erreur:
            print(erreur)


def demonstration(chaine, cles):
    # Les accords sont simulés dans cet exemple. Dans le menu, chacun répond.
    exemples = [
        Transaction("2026-11-27T12:00:00+01:00", "avance", "Alice", ("Benoît",), 2000, "Billet de train"),
        Transaction("2026-11-27T12:30:00+01:00", "achat", "Chloé", AMIS, 3000, "Déjeuner à trois"),
        Transaction("2026-11-27T14:00:00+01:00", "remboursement", "Benoît", ("Alice",), 800, "Premier remboursement"),
    ]
    for operation in exemples:
        proposer(chaine, operation, cles, lambda ami: True)
    chaine.valider()
    print("\nChaîne valide.")
    afficher_soldes(chaine, "Alice")
    afficher_historique(chaine, "Chloé")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--menu", action="store_true", help="ouvrir un carnet vide en mode interactif")
    args = parser.parse_args()
    cles = {ami: SigningKey.generate(curve=NIST384p) for ami in AMIS}
    chaine = Blockchain({ami: cle.verifying_key for ami, cle in cles.items()})
    if args.menu:
        menu(chaine, cles)
    else:
        demonstration(chaine, cles)


if __name__ == "__main__":
    main()
