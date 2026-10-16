# -*- coding: utf-8 -*-
"""Primitives pédagogiques du TP RSA. Petites clés publiques de l’énoncé.
Aucune garantie de sécurité, aucun usage en production.
Partie 1 : UTF-8 et SHA-256 signé en deux blocs, choix explicite documenté.
"""
import hashlib
import secrets
import statistics
import time
from dataclasses import dataclass


def home_mod_expnoent(x, y, n):
    """Partie 1 question 1a : calculer x**y modulo n sans pow.

    x : base entière ; y : exposant positif ou nul ; n : module positif.
    La boucle lit les bits de y de droite à gauche. À chaque tour, base
    représente la puissance de x associée au bit examiné. Seules les
    puissances correspondant aux bits à 1 sont multipliées au résultat.
    Exemple : 13 = 8 + 4 + 1, donc x**13 = x**8 * x**4 * x.
    """
    if n <= 0 or y < 0:
        raise ValueError("Il faut n > 0 et y >= 0.")
    resultat = 1 % n  # Le modulo traite aussi n=1 : tout reste vaut alors 0.
    base = x % n  # Réduire avant les multiplications limite les intermédiaires.
    exposant = y  # Copie locale pour ne pas modifier la valeur conceptuelle y.
    while exposant > 0:
        if exposant % 2 == 1:
            # Le bit courant est à 1 : inclure cette puissance dans le produit.
            resultat = (resultat * base) % n
        # Passer à la puissance suivante : x, x², x⁴, x⁸, etc.
        base = (base * base) % n
        # Division entière : supprimer le bit déjà traité, sans nombre flottant.
        exposant //= 2
    return resultat


def home_ext_euclide(y, b):
    """Renvoie l'inverse de b modulo y (ordre du squelette conserve).

    L'algorithme maintient r = s*y + t*b. A la fin, si le PGCD vaut 1,
    t*b est congru a 1 modulo y, donc t % y est l'inverse cherche.
    """
    if y <= 1:
        raise ValueError("Le module doit etre superieur a 1.")
    ancien_r, r = y, b % y
    # Coefficients initiaux de b : y contient 0*b, et b contient 1*b.
    ancien_t, t = 0, 1
    while r:
        quotient = ancien_r // r
        # Affectation simultanée Python : les deux membres de droite utilisent
        # les anciennes valeurs, comme si elles étaient sauvegardées d'abord.
        ancien_r, r = r, ancien_r - quotient * r
        # Appliquer au coefficient exactement la même transformation au reste.
        ancien_t, t = t, ancien_t - quotient * t
    if ancien_r != 1:
        raise ValueError("Pas d'inverse : les nombres ne sont pas premiers entre eux.")
    return ancien_t % y


def home_pgcd(a, b):
    """PGCD par Euclide : PGCD(a,b) = PGCD(b,a%b), jusqu'au reste nul."""
    while b:
        a, b = b, a % b
    return abs(a)


def home_string_to_int(texte):
    """Encoder le texte en UTF-8, puis lire ses octets comme un entier.

    Big-endian : l'octet de gauche porte le poids le plus fort.
    'AB' devient 65*256+66 = 16706. Un accent peut prendre plusieurs octets.
    """
    return int.from_bytes(texte.encode("utf-8"), "big")


def home_int_to_string(nombre, taille):
    """La taille en octets conserve les zeros initiaux et la chaine vide."""
    return nombre.to_bytes(taille, "big").decode("utf-8", errors="strict")


# Constantes originales du professeur.
x1a = 2010942103422233250095259520183
x2a = 3503815992030544427564583819137
x1b = 9434659759111223227678316435911
x2b = 8842546075387759637728590482297
na, nb = x1a * x2a, x1b * x2b
# Ces expressions sont lambda(n) (PPCM), et non phi(n) (produit).
lambda_a = (x1a - 1) * (x2a - 1) // home_pgcd(x1a - 1, x2a - 1)
lambda_b = (x1b - 1) * (x2b - 1) // home_pgcd(x1b - 1, x2b - 1)
ea, eb = 17, 23
da = home_ext_euclide(lambda_a, ea)
db = home_ext_euclide(lambda_b, eb)

# 256**L <= n garantit que tout bloc de L octets est inferieur a n.
LIMITE_MESSAGE = (na.bit_length() - 1) // 8  # 25 octets, pas caracteres
TAILLE_BLOC_HASH = (nb.bit_length() - 1) // 8  # 25 octets


@dataclass(frozen=True)
class Envoi:
    """Paquet simulé Bob → Alice, sans transport réseau.

    frozen=True empêche de changer ses champs accidentellement.
    La taille est nécessaire pour reconstruire les zéros initiaux du texte.
    signatures contient deux entiers pour les blocs SHA-256 de 25 et 7 octets.
    """
    chiffre: int
    taille_octets: int
    signatures: tuple


def home_blocs_hash(message):
    """Partie 1 question 3 : SHA-256 complet compatible avec les petites clés.

    SHA-256 produit 32 octets. Un bloc garanti sous nb fait ici 25 octets :
    on conserve donc 25 puis 7 octets au lieu de perdre les bits par un modulo.
    C'est une adaptation pédagogique explicite, pas RSA-PSS.
    """
    empreinte = hashlib.sha256(message.encode("utf-8")).digest()
    return tuple(empreinte[i:i + TAILLE_BLOC_HASH]
                 for i in range(0, len(empreinte), TAILLE_BLOC_HASH))


def home_envoyer(secret):
    """Partie 1 question 2 : Bob chiffre pour Alice et signe avec sa clé.

    Renvoie un Envoi contenant un seul chiffré, sa longueur et les signatures.
    La limite est en octets UTF-8, et non en nombre de caractères Python.
    """
    donnees = secret.encode("utf-8")
    if len(donnees) > LIMITE_MESSAGE:
        raise ValueError(f"Message trop long : {len(donnees)} octets UTF-8 ; "
                         f"limite : {LIMITE_MESSAGE} octets en partie 1.")
    num_sec = home_string_to_int(secret)
    if not 0 <= num_sec < na:
        raise ValueError("Le message doit etre strictement inferieur au module d'Alice.")
    chif = home_mod_expnoent(num_sec, ea, na)  # Confidentialité : clé publique Alice.
    # Chaque bloc de l'empreinte est signe avec la cle privee de Bob.
    signatures = tuple(home_mod_expnoent(int.from_bytes(bloc, "big"), db, nb)
                       for bloc in home_blocs_hash(secret))
    return Envoi(chif, len(donnees), signatures)


def home_recevoir(envoi):
    """Renvoie (message dechiffre, signature valide) ; rejette les formats invalides."""
    if not (0 <= envoi.chiffre < na and
            0 <= envoi.taille_octets <= LIMITE_MESSAGE):
        raise ValueError("Chiffre ou longueur invalide.")
    entier = home_mod_expnoent(envoi.chiffre, da, na)
    # Seule Alice utilise da. Le texte est ensuite reconstruit avec sa longueur.
    try:
        dechif = home_int_to_string(entier, envoi.taille_octets)
    except (OverflowError, UnicodeDecodeError) as erreur:
        raise ValueError("Message dechiffre incompatible avec le format UTF-8.") from erreur
    blocs = home_blocs_hash(dechif)
    # Alice recalcule le hash du texte reçu, sans faire confiance au hash de Bob.
    valide = len(envoi.signatures) == len(blocs)
    if valide:
        for signature, bloc in zip(envoi.signatures, blocs):
            if not 0 <= signature < nb:
                valide = False
                break
            obtenu = home_mod_expnoent(signature, eb, nb)
            # La clé publique de Bob retrouve l'entier qu'il a signé.
            if obtenu != int.from_bytes(bloc, "big"):
                valide = False
                break
    return dechif, valide


@dataclass(frozen=True)
class Trace:
    """Résultat numérique et observation pédagogique des opérations.

    bits_lsb contient les bits dans l'ordre du calcul (poids faible d'abord).
    carres compte tous les tours, y compris le dernier carré inutilisé ensuite.
    """
    resultat: int
    multiplications_conditionnelles: int
    carres: int
    bits_lsb: tuple


def home_mod_expnoent_trace(x, y, n):
    """Même calcul que partie 1 ; instrumente les branches, pas une sonde physique.

    bits_lsb est l'ordre chronologique de la boucle : bit faible en premier.
    Le total seul donne le poids de Hamming, pas les positions des bits.
    """
    if n <= 0 or y < 0:
        raise ValueError("Il faut n > 0 et y >= 0.")
    resultat, base, exposant = 1 % n, x % n, y
    bits = []
    while exposant:
        bit = exposant % 2
        # On enregistre volontairement la branche. Ce n'est pas une mesure
        # réelle de consommation électrique ou de cache d'un processeur.
        bits.append(bit)
        if bit:
            resultat = resultat * base % n
        base = base * base % n
        exposant //= 2
    return Trace(resultat, sum(bits), len(bits), tuple(bits))


@dataclass(frozen=True)
class ParametresCRT:
    """Paramètres privés précalculés, à garder secrets dans un vrai système.

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
    """Précondition RSA : p et q premiers distincts ; d strictement positif.

    Les premiers du professeur sont utilisés, pas une génération de clés.
    Les paramètres sont précalculés une seule fois pour la comparaison.
    """
    if min(p, q) < 2 or p == q or d <= 0 or home_pgcd(p, q) != 1:
        raise ValueError("Paramètres CRT invalides.")
    p, q = max(p, q), min(p, q)
    return ParametresCRT(p, q, d, d % (p - 1), d % (q - 1), home_ext_euclide(p, q))


def home_rsa_crt(c, parametres):
    """Partie 2 : calculer c**d modulo p*q par deux petits calculs.

    Le résidu final doit donner mp modulo p et mq modulo q.
    mq + h*q vaut déjà mq modulo q ; choisir h avec q_inv impose aussi mp.
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
    """00 || 02 || PS non nul || 00 || bloc, avec j <= k//2 et PS >= 8."""
    if not isinstance(bloc, bytes) or k < 11 or len(bloc) > min(k // 2, k - 11):
        raise ValueError("Bloc ou taille de bourrage invalide.")
    # Équivalent au domaine alea % 255 + 1, sans biais de réduction.
    ps = bytes(secrets.randbelow(255) + 1 for _ in range(k - len(bloc) - 3))
    return b"\x00\x02" + ps + b"\x00" + bloc


def home_debourrer(bloc, k=K_BLOC):
    """Erreur générique. Ce parsing Python n'est pas à temps constant."""
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
    chiffres: tuple
    signatures: tuple


def home_envoyer_blocs(secret):
    """Partie 3 : découper, bourrer, chiffrer et signer un texte long.

    Le découpage porte sur les octets, donc peut couper un caractère UTF-8.
    Cela reste correct car Alice concatène les octets avant de décoder.
    """
    donnees = secret.encode("utf-8")
    # Le message vide est représenté par un bloc bourré, pas par un paquet vide.
    morceaux = [donnees[i:i + J_MESSAGE] for i in range(0, len(donnees), J_MESSAGE)] or [b""]
    chiffres = []
    for morceau in morceaux:
        # Le padding ajoute un aléa : deux envois du même texte diffèrent.
        nombre = int.from_bytes(home_bourrer(morceau), "big")
        if nombre >= na:
            raise ValueError("Le bloc bourré dépasse le module RSA.")
        chiffres.append(home_mod_expnoent(nombre, ea, na))
    signatures = tuple(home_rsa_crt(int.from_bytes(bloc, "big"), CRT_BOB)
                       for bloc in home_blocs_hash(secret))
    return EnvoiBlocs(tuple(chiffres), signatures)


def home_recevoir_blocs(envoi, utiliser_crt=True):
    """Partie 3 : déchiffrer chaque bloc puis vérifier le texte complet.

    utiliser_crt=False permet une comparaison au calcul direct dans les tests.
    Le retour est (texte, signature_valide) ; un format illisible lève une erreur.
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
    """Bonus : médianes en ns, sur cette machine, sans promesse de gain.

    Retourne aussi le poids de Hamming, constant pour un exposant fixé.
    Les temps Python ne sont pas des mesures physiques de consommation.
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
        td, tc = statistics.median(direct), statistics.median(crt)
        resultats.append({"message": message, "direct_ns": round(td), "crt_ns": round(tc),
                          "rapport_direct_sur_crt": round(td / tc, 3),
                          "multiplications_conditionnelles": da.bit_count(),
                          "bits_exposant": da.bit_length(), "series": series,
                          "repetitions_par_serie": repetitions})
    return resultats


