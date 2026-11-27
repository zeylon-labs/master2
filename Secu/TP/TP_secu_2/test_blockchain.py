import hashlib
import io
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from unittest.mock import patch

from ecdsa import NIST384p, SigningKey

import Partie1_Walter_Arthur as p1
import Partie2_Walter as p2


class TestCarnetPersonnel(unittest.TestCase):
    def setUp(self):
        self.cle = SigningKey.generate(curve=NIST384p)
        self.chaine = p1.Blockchain(self.cle.verifying_key)
        self.texte = "J'ai dépensé 70 € chez Total"
        self.signature = self.cle.sign_deterministic(self.texte.encode(), hashfunc=hashlib.sha256)

    def test_bloc_signe_et_mine(self):
        self.chaine.create_block_from_transaction([self.texte], [self.signature])
        bloc = self.chaine.last_block
        self.assertEqual(bloc.previous_block_hash, self.chaine.chain[0].block_hash)
        self.assertEqual(bloc.block_hash, p1.empreinte(bloc.prefixe_minage(), bloc.nonce))
        self.assertTrue(bloc.block_hash.startswith("00"))

    def test_signature_liee_au_libelle_et_a_la_cle(self):
        autre = SigningKey.generate(curve=NIST384p).verifying_key
        self.assertFalse(p1.verifier_signature(autre, self.texte, self.signature))
        with self.assertRaises(ValueError):
            self.chaine.create_block_from_transaction([self.texte.replace("70", "700")], [self.signature])
        with self.assertRaises(ValueError):
            self.chaine.create_block_from_transaction([self.texte], [])
        self.assertEqual(len(self.chaine.chain), 1)

    def test_mesure_annonce_une_preuve_recalculable(self):
        bloc = self.chaine.last_block
        with redirect_stdout(io.StringIO()):
            zeros, nonce, digest = p1.mesurer_minage(bloc, 0.01)
        self.assertEqual(digest, p1.empreinte(bloc.prefixe_minage(), nonce))
        self.assertEqual(zeros, len(digest) - len(digest.lstrip("0")))


class TestTroisAmis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cles = {a: SigningKey.generate(curve=NIST384p) for a in p2.AMIS}

    def setUp(self):
        self.chaine = p2.Blockchain({a: cle.verifying_key for a, cle in self.cles.items()})
        self.avance = p2.Transaction("2026-11-27T12:00:00+01:00", "avance",
                                     "Alice", ("Benoît",), 2000, "Billet")

    def signer(self, op):
        return {a: self.cles[a].sign_deterministic(op.message(self.chaine.derniere_empreinte),
                                                  hashfunc=hashlib.sha256).hex()
                for a in op.participants()}

    def ajouter(self, op):
        self.chaine.ajouter(op, self.signer(op))

    def test_soldes_et_historique(self):
        self.ajouter(self.avance)
        achat = replace(self.avance, nature="achat", payeur="Chloé", beneficiaires=p2.AMIS, centimes=3000)
        self.ajouter(achat)
        retour = replace(self.avance, nature="remboursement", payeur="Benoît",
                         beneficiaires=("Alice",), centimes=800)
        self.ajouter(retour)
        soldes = self.chaine.valider()
        self.assertEqual(soldes["Alice"], {"Benoît": 1200, "Chloé": -1000})
        self.assertEqual(soldes["Benoît"], {"Alice": -1200, "Chloé": -1000})
        self.assertEqual(soldes["Chloé"], {"Alice": 1000, "Benoît": 1000})
        self.assertEqual(self.chaine.historique("Chloé"), [achat])
        self.assertEqual(self.chaine.historique("Alice"), [self.avance, achat, retour])

    def test_partage_au_centime(self):
        achat = replace(self.avance, nature="achat", payeur="Chloé", beneficiaires=p2.AMIS, centimes=1000)
        self.assertEqual(achat.parts(), {"Alice": 334, "Benoît": 333, "Chloé": 333})
        self.ajouter(achat)
        self.assertEqual(self.chaine.valider()["Chloé"], {"Alice": 334, "Benoît": 333})

    def test_refus_sans_ajout(self):
        with redirect_stdout(io.StringIO()):
            accepte = p2.proposer(self.chaine, self.avance, self.cles, lambda a: a != "Benoît")
        self.assertFalse(accepte)
        self.assertEqual(len(self.chaine.blocs), 1)

    def test_parcours_du_menu(self):
        saisie = ["1", "avance", "1", "2", "20,00", "Billet", "o", "n", "2",
                  "1", "avance", "1", "2", "20", "Billet", "o", "oui",
                  "3", "1", "4", "3", "2", "0"]
        sortie = io.StringIO()
        with patch("builtins.input", side_effect=saisie), redirect_stdout(sortie):
            p2.menu(self.chaine, self.cles)
        for attendu in ("Benoît refuse", "Opérations enregistrées : 0.",
                        "Benoît doit 20,00 € à Alice.", "Historique pour Chloé\nAucune opération.",
                        "Opérations enregistrées : 1."):
            self.assertIn(attendu, sortie.getvalue())

    def test_signataires_exacts(self):
        signatures = self.signer(self.avance)
        for accords in ({"Alice": signatures["Alice"]},
                        {**signatures, "Chloé": signatures["Benoît"]},
                        {**signatures, "Benoît": signatures["Alice"]}):
            with self.subTest(signataires=list(accords)), self.assertRaises(ValueError):
                self.chaine.ajouter(self.avance, accords)
        self.assertEqual(len(self.chaine.blocs), 1)

    def test_signature_couvre_date_motif_somme_et_beneficiaire(self):
        accords = self.signer(self.avance)
        for changement in ({"date": "2026-11-28T12:00:00+01:00"}, {"motif": "Taxi"},
                           {"centimes": 2001}, {"beneficiaires": ("Chloé",)}):
            with self.subTest(changement=changement), self.assertRaises(ValueError):
                self.chaine.ajouter(replace(self.avance, **changement), accords)

    def test_deuxieme_presentation_des_memes_accords(self):
        accords = self.signer(self.avance)
        self.chaine.ajouter(self.avance, accords)
        with self.assertRaises(ValueError):
            self.chaine.ajouter(self.avance, accords)

    def test_remboursement_limite_a_la_dette(self):
        self.ajouter(self.avance)
        retour = replace(self.avance, nature="remboursement", payeur="Benoît", beneficiaires=("Alice",))
        with self.assertRaises(ValueError):
            self.ajouter(replace(retour, centimes=2001))
        self.ajouter(retour)
        self.assertEqual(self.chaine.valider()["Alice"]["Benoît"], 0)
        with self.assertRaises(ValueError):
            self.ajouter(replace(retour, centimes=1))

    def test_validation_des_liens_et_de_la_preuve(self):
        self.ajouter(self.avance)
        bloc = self.chaine.blocs[-1]
        bloc.precedent = "0"
        with self.assertRaisesRegex(ValueError, "Lien"):
            self.chaine.valider()
        bloc.precedent = self.chaine.blocs[0].empreinte
        while bloc.empreinte.startswith("00"):
            bloc.nonce += 1
            bloc.empreinte = bloc.hacher(bloc.prefixe())
        with self.assertRaisesRegex(ValueError, "Preuve"):
            self.chaine.valider()

    def test_operation_modifiee_apres_ajout(self):
        self.ajouter(self.avance)
        bloc = self.chaine.blocs[-1]
        bloc.operation = replace(self.avance, centimes=9999)
        with self.assertRaisesRegex(ValueError, "Empreinte"):
            self.chaine.valider()
        bloc.miner()
        with self.assertRaisesRegex(ValueError, "Signature"):
            self.chaine.valider()

    def test_regles_de_saisie(self):
        for texte in ("2,50", "2.5"):
            self.assertEqual(p2.lire_montant(texte), 250)
        for texte in ("-2", "0", "0.001", "NaN", "deux"):
            with self.subTest(texte=texte), self.assertRaises(ValueError):
                p2.lire_montant(texte)
        for changement in ({"beneficiaires": ("Alice",)}, {"beneficiaires": ("Inconnu",)},
                           {"nature": "achat", "beneficiaires": ("Alice", "Alice")},
                           {"motif": " "}, {"date": "2026-11-27"}, {"centimes": -5}):
            with self.subTest(changement=changement), self.assertRaises(ValueError):
                replace(self.avance, **changement).verifier()


if __name__ == "__main__":
    unittest.main()
