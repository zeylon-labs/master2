# -*- coding: utf-8 -*-
"""Fonctions de calcul utilisées dans les trois parties du TP RSA.

Les clés sont celles de l'énoncé. Le texte est encodé en UTF-8.
La signature SHA-256 utilise deux blocs car le module de Bob est trop petit
pour contenir les 32 octets à la fois. Il s'agit d'une adaptation au TP,
pas d'un schéma de signature à utiliser dans une application.
"""
import hashlib
import secrets
import statistics
import time
from dataclasses import dataclass


def home_mod_expnoent(x, y, n):
    """Calculer x puissance y modulo n sans construire toute la puissance.

    On parcourt les bits de l'exposant de droite à gauche. Un bit à 1
    indique qu'il faut multiplier le résultat par la puissance en cours.
    Par exemple, 13 = 8 + 4 + 1 : x**13 utilise x**8, x**4 et x.
    Le modulo après chaque produit évite de garder des nombres trop grands.
    """
    if n <= 0 or y < 0:
        raise ValueError("Il faut n > 0 et y >= 0.")
    resultat = 1 % n  # Pour n=1, le reste doit être 0, même si y vaut 0.
    base = x % n
    exposant = y
    while exposant > 0:
        if exposant % 2 == 1:
            # Exposant impair : la puissance courante participe au résultat.
            resultat = (resultat * base) % n
        # Préparer les puissances successives : x, x², x⁴, x⁸...
        base = (base * base) % n
        # En divisant par deux, on passe au bit suivant.
        exposant //= 2
    return resultat


def home_ext_euclide(y, b):
    """Trouver le nombre qui, multiplié par b, laisse un reste de 1 modulo y.

    Le module vient en premier, comme dans le code de départ du TP :
    home_ext_euclide(20, 3) donne 7 car 3*7 = 20+1.
    Les divisions d'Euclide donnent le PGCD et le coefficient utile.
    Si le PGCD n'est pas 1, l'inverse n'existe pas.
    """
    if y <= 1:
        raise ValueError("Le module doit etre superieur a 1.")
    ancien_r, r = y, b % y
    # Au départ, le coefficient de b est 0 dans y et 1 dans b.
    ancien_t, t = 0, 1
    while r:
        quotient = ancien_r // r
        ancien_r, r = r, ancien_r - quotient * r
        # Mettre à jour le coefficient avec la même division.
        ancien_t, t = t, ancien_t - quotient * t
    if ancien_r != 1:
        raise ValueError("Pas d'inverse : les nombres ne sont pas premiers entre eux.")
    return ancien_t % y


def home_pgcd(a, b):
    """Calculer le PGCD en répétant les divisions jusqu'au reste nul."""
    while b:
        a, b = b, a % b
    return abs(a)


def home_string_to_int(texte):
    """Passer du texte à un entier sur lequel RSA peut travailler.

    Avec l'ordre big-endian, 'AB' vaut 65*256+66, soit 16706.
    On compte les octets UTF-8 : 'é' prend deux octets, même si c'est une lettre.
    """
    return int.from_bytes(texte.encode("utf-8"), "big")


def home_int_to_string(nombre, taille):
    """Retrouver le texte, en gardant la longueur exacte de ses octets.

    La taille permet de remettre les éventuels octets nuls au début.
    Elle distingue aussi une chaîne vide d'une chaîne contenant un zéro.
    """
    return nombre.to_bytes(taille, "big").decode("utf-8", errors="strict")


# Nombres fournis dans l'énoncé : on garde les mêmes clés pour tout le TP.
x1a = 2010942103422233250095259520183
x2a = 3503815992030544427564583819137
x1b = 9434659759111223227678316435911
x2b = 8842546075387759637728590482297
na, nb = x1a * x2a, x1b * x2b
# Le TP utilise le PPCM de p-1 et q-1, donc lambda(n).
lambda_a = (x1a - 1) * (x2a - 1) // home_pgcd(x1a - 1, x2a - 1)
lambda_b = (x1b - 1) * (x2b - 1) // home_pgcd(x1b - 1, x2b - 1)
ea, eb = 17, 23
da = home_ext_euclide(lambda_a, ea)
db = home_ext_euclide(lambda_b, eb)

# Choisir L pour que n'importe quel bloc de L octets représente un entier < n.
LIMITE_MESSAGE = (na.bit_length() - 1) // 8  # 25 octets UTF-8
TAILLE_BLOC_HASH = (nb.bit_length() - 1) // 8  # 25 octets


@dataclass(frozen=True)
class Envoi:
    """Les valeurs que Bob transmet à Alice dans la première partie.

    La longueur conserve les éventuels zéros au début du message.
    Les deux signatures correspondent aux deux blocs du SHA-256.
    """
    chiffre: int
    taille_octets: int
    signatures: tuple


def home_blocs_hash(message):
    """Calculer le SHA-256 du texte et le répartir sur deux blocs.

    Les 32 octets ne tiennent pas toujours dans le module de Bob.
    On garde donc 25 octets puis les 7 restants, sans perdre de partie du hash.
    Cette adaptation convient aux calculs du TP ; ce n'est pas RSA-PSS.
    """
    empreinte = hashlib.sha256(message.encode("utf-8")).digest()
    return tuple(empreinte[i:i + TAILLE_BLOC_HASH]
                 for i in range(0, len(empreinte), TAILLE_BLOC_HASH))


def home_envoyer(secret):
    """Préparer le message de Bob pour Alice.

    Le message est chiffré avec la clé publique d'Alice, puis le hash est
    signé avec la clé privée de Bob. Cette partie utilise un seul bloc
    de message, limité à 25 octets UTF-8.
    """
    donnees = secret.encode("utf-8")
    if len(donnees) > LIMITE_MESSAGE:
        raise ValueError(f"Message trop long : {len(donnees)} octets UTF-8 ; "
                         f"limite : {LIMITE_MESSAGE} octets en partie 1.")
    message_entier = home_string_to_int(secret)
    if not 0 <= message_entier < na:
        raise ValueError("Le message doit etre strictement inferieur au module d'Alice.")
    chiffre = home_mod_expnoent(message_entier, ea, na)
    # Bob utilise sa propre clé privée pour signer les deux blocs du hash.
    signatures = tuple(home_mod_expnoent(int.from_bytes(bloc, "big"), db, nb)
                       for bloc in home_blocs_hash(secret))
    return Envoi(chiffre, len(donnees), signatures)


def home_recevoir(envoi):
    """Lire l'envoi côté Alice et vérifier les signatures de Bob.

    On renvoie le texte retrouvé et un booléen pour la signature.
    Si le format ne permet pas de reconstruire le texte, on signale une erreur.
    """
    if not (0 <= envoi.chiffre < na and
            0 <= envoi.taille_octets <= LIMITE_MESSAGE):
        raise ValueError("Chiffre ou longueur invalide.")
    entier = home_mod_expnoent(envoi.chiffre, da, na)
    # Alice utilise son exposant privé da pour retrouver le message.
    try:
        texte = home_int_to_string(entier, envoi.taille_octets)
    except (OverflowError, UnicodeDecodeError) as erreur:
        raise ValueError("Message dechiffre incompatible avec le format UTF-8.") from erreur
    blocs = home_blocs_hash(texte)
    valide = len(envoi.signatures) == len(blocs)
    if valide:
        for signature, bloc in zip(envoi.signatures, blocs):
            if not 0 <= signature < nb:
                valide = False
                break
            obtenu = home_mod_expnoent(signature, eb, nb)
            # La vérification utilise la clé publique de Bob, pas celle d'Alice.
            if obtenu != int.from_bytes(bloc, "big"):
                valide = False
                break
    return texte, valide


@dataclass(frozen=True)
class Trace:
    """Le résultat du calcul, avec les opérations que l'on a comptées.

    bits_lsb contient les bits dans l'ordre du calcul (poids faible d'abord).
    carres compte tous les tours, y compris le dernier carré inutilisé ensuite.
    """
    resultat: int
    multiplications_conditionnelles: int
    carres: int
    bits_lsb: tuple


def home_mod_expnoent_trace(x, y, n):
    """Refaire le calcul en notant les bits qui déclenchent une multiplication.

    La liste commence par le bit de poids faible, car la boucle part de droite.
    Le total donne le nombre de bits à 1, pas leur position. C'est une
    simulation dans le code, pas une mesure de consommation électrique.
    """
    if n <= 0 or y < 0:
        raise ValueError("Il faut n > 0 et y >= 0.")
    resultat, base, exposant = 1 % n, x % n, y
    bits = []
    while exposant:
        bit = exposant % 2
        # Garder le bit pour relire ensuite l'ordre des opérations.
        bits.append(bit)
        if bit:
            resultat = resultat * base % n
        base = base * base % n
        exposant //= 2
    return Trace(resultat, sum(bits), len(bits), tuple(bits))


@dataclass(frozen=True)
class ParametresCRT:
    """Les valeurs que l'on prépare une fois pour utiliser le CRT.

    p,q : facteurs premiers ; d : exposant privé ; dp,dq : exposants réduits ;
    q_inv : inverse de q modulo p, utilisé pour recombiner les deux résidus.
    """
    p: int
    q: int
    d: int
    dp: int
    dq: int
    q_inv: int


def home_preparer_crt(p, q, d):
    """Préparer les deux petits calculs qui remplacent le calcul modulo p*q.

    Dans le TP, p et q sont des premiers distincts déjà fournis et d > 0.
    On réduit d modulo p-1 et q-1, puis on calcule l'inverse de q modulo p.
    Ces valeurs sont réutilisées à chaque déchiffrement.
    """
    if min(p, q) < 2 or p == q or d <= 0 or home_pgcd(p, q) != 1:
        raise ValueError("Paramètres CRT invalides.")
    p, q = max(p, q), min(p, q)
    return ParametresCRT(p, q, d, d % (p - 1), d % (q - 1), home_ext_euclide(p, q))


def home_rsa_crt(c, parametres):
    """Déchiffrer avec le CRT, puis réunir les deux résultats.

    mp et mq sont les restes du même message, pas deux morceaux du texte.
    On cherche un entier qui donne mp modulo p et mq modulo q.
    Le terme h sert à satisfaire les deux conditions en même temps.
    """
    p, q = parametres.p, parametres.q
    if not 0 <= c < p * q:
        raise ValueError("Entier RSA hors du domaine.")
    # Le cas c divisible par un premier doit rester 0, même si dp/dq = 0.
    mp = 0 if c % p == 0 else home_mod_expnoent(c, parametres.dp, p)
    mq = 0 if c % q == 0 else home_mod_expnoent(c, parametres.dq, q)
    h = (mp - mq) * parametres.q_inv % p  # Ajustement pour satisfaire le modulo p.
    return (mq + h * q) % (p * q)


CRT_ALICE = home_preparer_crt(x1a, x2a, da)
CRT_BOB = home_preparer_crt(x1b, x2b, db)
K_BLOC = (na.bit_length() + 7) // 8  # 26 octets
# Trois octets de structure (00,02,séparateur) et au moins huit octets PS.
# min respecte à la fois la règle j<=k/2 du sujet et PS>=8 de PKCS#1 v1.5.
J_MESSAGE = min(K_BLOC // 2, K_BLOC - 11)  # 13 octets ; PS >= 8


def home_bourrer(bloc, k=K_BLOC):
    """Ajouter le préfixe et les octets aléatoires autour d'un morceau.

    Le bloc final est 00 || 02 || PS || 00 || message.
    Avec k=26 et 13 octets de message, il reste 10 octets pour PS.
    """
    if not isinstance(bloc, bytes) or k < 11 or len(bloc) > min(k // 2, k - 11):
        raise ValueError("Bloc ou taille de bourrage invalide.")
    # Les octets de PS sont non nuls : le zéro marque la fin du bourrage.
    ps = bytes(secrets.randbelow(255) + 1 for _ in range(k - len(bloc) - 3))
    return b"\x00\x02" + ps + b"\x00" + bloc


def home_debourrer(bloc, k=K_BLOC):
    """Vérifier la forme du bloc et ne garder que le morceau du message.

    Une erreur donne le même texte, quel que soit le contrôle qui échoue.
    Cela ne garantit pas pour autant un temps d'exécution constant.
    """
    erreur = "Bloc chiffré invalide."
    if not isinstance(bloc, bytes) or len(bloc) != k or k < 11:
        raise ValueError(erreur)
    # Le premier 00 après le préfixe termine PS. Si sa position est 10 ou
    # plus, PS contient au moins huit octets : indices 2 à 9 inclus.
    separateur = bloc.find(b"\x00", 2)
    if bloc[:2] != b"\x00\x02" or separateur < 10:
        raise ValueError(erreur)
    message = bloc[separateur + 1:]
    if len(message) > min(k // 2, k - 11):
        raise ValueError(erreur)
    return message


@dataclass(frozen=True)
class EnvoiBlocs:
    """L'envoi complet : les blocs chiffrés et les signatures du texte."""
    chiffres: tuple
    signatures: tuple


def home_envoyer_blocs(secret):
    """Préparer un envoi sans la limite d'un seul bloc de message.

    On découpe les octets et on chiffre chaque morceau après bourrage.
    Un caractère peut être coupé entre deux blocs : Alice réunira les octets
    avant de les décoder, pour retrouver le texte sans l'abîmer.
    """
    donnees = secret.encode("utf-8")
    # Le message vide est représenté par un bloc bourré, pas par un paquet vide.
    morceaux = [donnees[i:i + J_MESSAGE] for i in range(0, len(donnees), J_MESSAGE)] or [b""]
    chiffres = []
    for morceau in morceaux:
        # Ajouter un nouveau bourrage aléatoire pour chaque morceau.
        nombre = int.from_bytes(home_bourrer(morceau), "big")
        if nombre >= na:
            raise ValueError("Le bloc bourré dépasse le module RSA.")
        chiffres.append(home_mod_expnoent(nombre, ea, na))
    signatures = tuple(home_rsa_crt(int.from_bytes(bloc, "big"), CRT_BOB)
                       for bloc in home_blocs_hash(secret))
    return EnvoiBlocs(tuple(chiffres), signatures)


def home_recevoir_blocs(envoi, utiliser_crt=True):
    """Retrouver les morceaux côté Alice et les remettre dans l'ordre reçu.

    On peut désactiver le CRT pour comparer avec le calcul direct.
    Une fois les octets réunis, on décode le texte et on vérifie son hash signé.
    Le retour est (texte, signature_valide).
    """
    if not envoi.chiffres:
        raise ValueError("Bloc chiffré invalide.")
    donnees = bytearray()
    for c in envoi.chiffres:
        if not 0 <= c < na:
            raise ValueError("Bloc chiffré invalide.")
        nombre = home_rsa_crt(c, CRT_ALICE) if utiliser_crt else home_mod_expnoent(c, da, na)
        try:
            # La taille fixe rétablit l'octet 00 initial perdu dans l'entier.
            morceau = home_debourrer(nombre.to_bytes(K_BLOC, "big"))
        except (ValueError, OverflowError) as erreur:
            raise ValueError("Bloc chiffré invalide.") from erreur
        donnees.extend(morceau)  # Accumuler les octets sans les décoder séparément.
    try:
        texte = donnees.decode("utf-8", errors="strict")
    except UnicodeDecodeError as erreur:
        raise ValueError("Bloc chiffré invalide.") from erreur
    attendus = home_blocs_hash(texte)  # Vérification après concaténation complète.
    valide = len(envoi.signatures) == len(attendus)
    if valide:
        valide = all(0 <= s < nb and home_mod_expnoent(s, eb, nb) == int.from_bytes(b, "big")
                     for s, b in zip(envoi.signatures, attendus))
    return texte, valide


def home_comparer_temps(messages, repetitions=30, series=5):
    """Chronométrer le calcul direct et le CRT sur plusieurs messages.

    On fait plusieurs séries pour éviter de se fier à une mesure isolée.
    Les temps dépendent de la machine ; ils ne constituent pas une mesure
    physique de fuite de la clé. Le compte des bits à 1 est gardé à part.
    """
    if repetitions < 1 or series < 1:
        raise ValueError("Le nombre de répétitions et de séries doit être positif.")
    resultats = []
    for message in messages:
        if not 0 <= message < na:
            raise ValueError("Message hors domaine.")
        c = home_mod_expnoent(message, ea, na)
        direct, crt = [], []
        assert home_mod_expnoent(c, da, na) == home_rsa_crt(c, CRT_ALICE)
        for serie in range(series):
            fonctions = [(direct, lambda: home_mod_expnoent(c, da, na)),
                         (crt, lambda: home_rsa_crt(c, CRT_ALICE))]
            if serie % 2:
                fonctions.reverse()
            for mesures, calcul in fonctions:
                debut = time.perf_counter_ns()
                for _ in range(repetitions):
                    calcul()
                mesures.append((time.perf_counter_ns() - debut) / repetitions)
        temps_direct = statistics.median(direct)
        temps_crt = statistics.median(crt)
        resultats.append({"message": message, "direct_ns": round(temps_direct), "crt_ns": round(temps_crt),
                          "rapport_direct_sur_crt": round(temps_direct / temps_crt, 3),
                          "multiplications_conditionnelles": da.bit_count(),
                          "bits_exposant": da.bit_length(), "series": series,
                          "repetitions_par_serie": repetitions})
    return resultats
