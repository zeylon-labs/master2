"""Tests reproductibles ; pow est uniquement une référence de test."""
from dataclasses import replace
from pathlib import Path
import hashlib
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import Walter_Arthur_util as u


class Partie1(unittest.TestCase):
    def test_exponentiation(self):
        rng = random.Random(20261016)
        for _ in range(300):
            x, y, n = rng.randrange(-10000, 10000), rng.randrange(1000), rng.randrange(1, 10000)
            self.assertEqual(u.home_mod_expnoent(x, y, n), pow(x, y, n))
        self.assertEqual(u.home_mod_expnoent(0, 0, 1), 0)
        for arguments in [(2, -1, 5), (2, 3, 0)]:
            with self.assertRaises(ValueError):
                u.home_mod_expnoent(*arguments)

    def test_inverses(self):
        self.assertEqual(u.home_ext_euclide(3120, 17), 2753)
        for module in range(2, 70):
            for nombre in range(1, module):
                if u.home_pgcd(module, nombre) == 1:
                    self.assertEqual(nombre * u.home_ext_euclide(module, nombre) % module, 1)
                else:
                    with self.assertRaises(ValueError):
                        u.home_ext_euclide(module, nombre)
        self.assertEqual(u.ea * u.da % u.lambda_a, 1)
        self.assertEqual(u.eb * u.db % u.lambda_b, 1)

    def test_echanges_utf8(self):
        for texte in ["Bonjour Alice", "", "\x00Alice", "\x00", "école", "😀", "A" * 25, "é" * 12 + "A"]:
            self.assertEqual(u.home_recevoir(u.home_envoyer(texte)), (texte, True))

    def test_limites_et_hash(self):
        self.assertLess(256 ** u.LIMITE_MESSAGE - 1, u.na)
        self.assertGreater(256 ** (u.LIMITE_MESSAGE + 1) - 1, u.na)
        for texte in ["A" * 26, "é" * 13]:
            with self.assertRaises(ValueError):
                u.home_envoyer(texte)
        blocs = u.home_blocs_hash("Bonjour Alice")
        self.assertEqual([len(b) for b in blocs], [25, 7])
        self.assertEqual(b"".join(blocs), hashlib.sha256(b"Bonjour Alice").digest())

    def test_alterations(self):
        envoi = u.home_envoyer("Bonjour Alice")
        mauvaises = ((envoi.signatures[0] + 1) % u.nb,) + envoi.signatures[1:]
        for signatures in [mauvaises, envoi.signatures[:1], (u.nb, 0)]:
            self.assertFalse(u.home_recevoir(replace(envoi, signatures=signatures))[1])
        autre = u.home_envoyer("Bonjour Bob")
        self.assertFalse(u.home_recevoir(replace(autre, signatures=envoi.signatures))[1])
        for paquet in [replace(envoi, chiffre=u.na), replace(envoi, taille_octets=26),
                       replace(envoi, taille_octets=0)]:
            with self.assertRaises(ValueError):
                u.home_recevoir(paquet)


class Partie2(unittest.TestCase):
    def test_trace_et_bits(self):
        for exposant in range(100):
            trace = u.home_mod_expnoent_trace(42, exposant, 101)
            self.assertEqual(trace.resultat, pow(42, exposant, 101))
            self.assertEqual(trace.multiplications_conditionnelles, exposant.bit_count())
            self.assertEqual(trace.carres, exposant.bit_length())
            self.assertEqual(sum(bit << i for i, bit in enumerate(trace.bits_lsb)), exposant)
        self.assertEqual(u.home_mod_expnoent_trace(3, 13, 17).bits_lsb, (1, 0, 1, 1))
        # 11 et 13 ont même poids et longueur, mais des positions différentes.
        a, b = [u.home_mod_expnoent_trace(42, e, 101) for e in [11, 13]]
        self.assertEqual(a.multiplications_conditionnelles, b.multiplications_conditionnelles)
        self.assertNotEqual(a.bits_lsb, b.bits_lsb)

    def test_trace_independante_message(self):
        traces = [u.home_mod_expnoent_trace(c, u.da, u.na) for c in [0, 1, 42, 513, u.na - 1]]
        self.assertEqual(len({t.bits_lsb for t in traces}), 1)

    def test_crt_exemple_officiel(self):
        config = u.home_preparer_crt(137, 131, 11787)
        self.assertEqual((config.dp, config.dq, config.q_inv), (91, 87, 114))
        self.assertEqual(u.home_rsa_crt(8363, config), 513)
        self.assertEqual(u.home_mod_expnoent(513, 3, 17947), 8363)

    def test_crt_cles_professeur(self):
        rng = random.Random(1234)
        for config in [u.CRT_ALICE, u.CRT_BOB]:
            n = config.p * config.q
            for c in [0, 1, config.p, config.q, n - 1] + [rng.randrange(n) for _ in range(80)]:
                self.assertEqual(u.home_rsa_crt(c, config), pow(c, config.d, n))

    def test_crt_exposant_reduit_zero(self):
        config = u.home_preparer_crt(5, 7, 12)
        for c in range(35):
            self.assertEqual(u.home_rsa_crt(c, config), pow(c, 12, 35))
        for c in [-1, 35]:
            with self.assertRaises(ValueError):
                u.home_rsa_crt(c, config)


class Partie3(unittest.TestCase):
    def test_structure_bourrage(self):
        for j in range(u.J_MESSAGE + 1):
            message = bytes(range(j))
            bloc = u.home_bourrer(message)
            self.assertEqual(len(bloc), 26)
            self.assertEqual(bloc[:2], b"\x00\x02")
            position = bloc.find(b"\x00", 2)
            self.assertEqual(position, 26 - j - 1)
            self.assertTrue(all(bloc[2:position]))
            self.assertGreaterEqual(position - 2, 8)
            self.assertLess(int.from_bytes(bloc, "big"), u.na)
            self.assertEqual(u.home_debourrer(bloc), message)

    def test_bourrage_invalide(self):
        bon = u.home_bourrer(b"Bonjour")
        invalides = [bon[:-1], b"\x01" + bon[1:], b"\x00\x01" + bon[2:],
                     b"\x00\x02" + b"\x01" * 24,
                     b"\x00\x02" + b"\x01" * 7 + b"\x00" + b"A" * 16,
                     b"\x00\x02" + b"\x01" * 8 + b"\x00" + b"A" * 15]
        for bloc in invalides:
            with self.assertRaisesRegex(ValueError, "Bloc chiffré invalide"):
                u.home_debourrer(bloc)
        with self.assertRaises(ValueError):
            u.home_bourrer(b"A" * 14)

    def test_messages_multiblocs(self):
        for message in ["", "\x00", "A" * 13, "A" * 14, "A" * 26,
                        "A" * 12 + "😀" + "école", "Bonjour Alice ! " * 30,
                        "\x00début\x00milieu\x00fin\x00"]:
            paquet = u.home_envoyer_blocs(message)
            attendu = (message, True)
            self.assertEqual(u.home_recevoir_blocs(paquet), attendu)
            self.assertEqual(u.home_recevoir_blocs(paquet, utiliser_crt=False), attendu)

    def test_aleatoire(self):
        # Collision astronomiquement improbable, contrairement à un test de temps.
        a, b = u.home_envoyer_blocs("Bonjour"), u.home_envoyer_blocs("Bonjour")
        self.assertNotEqual(a.chiffres, b.chiffres)
        self.assertEqual(a.signatures, b.signatures)  # signature brute déterministe

    def test_alterations(self):
        paquet = u.home_envoyer_blocs("A" * 13 + "B" * 13 + "C" * 13)
        for chiffres in [paquet.chiffres[::-1], paquet.chiffres[:-1], paquet.chiffres * 2]:
            self.assertFalse(u.home_recevoir_blocs(replace(paquet, chiffres=chiffres))[1])
        self.assertFalse(u.home_recevoir_blocs(replace(paquet, signatures=()))[1])
        for chiffres in [(), (0,), (u.na,), (-1,)]:
            with self.assertRaisesRegex(ValueError, "Bloc chiffré invalide"):
                u.home_recevoir_blocs(replace(paquet, chiffres=chiffres))


if __name__ == "__main__":
    unittest.main()
