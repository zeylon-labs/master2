# TP RSA Sécurité et Pratiques

Arthur Walter · Master 2 Data Science

Sécurité des systèmes d'information · Abdeljalil ABBAS-TURKI · 16 octobre 2026

# Partie 1 Implémentation de base du RSA

## Question 1a Compléter l’exponentiation modulaire rapide

La fonction home_mod_expnoent(x, y, n) calcule x puissance y modulo n. Elle évite de construire toute la puissance : elle utilise des carrés successifs et ne multiplie au résultat que les puissances nécessaires. Pour cela, l’exposant est lu en binaire, de droite à gauche.

À chaque multiplication, on ne garde que le reste de la division par n. Par exemple, 17 modulo 5 vaut 2, puisque 17 = 3 × 5 + 2. De même, 2 puissance 3 modulo 5 donne 3 : on calcule 8, puis son reste dans la division par 5. Le nombre de tours de la boucle correspond à la longueur de l’exposant en bits.

Pour x = 3, y = 13 et n = 17, la fonction retourne 12. Comme 13 s’écrit 1101 en binaire, le calcul utilise trois multiplications conditionnelles. Les tests comparent également 300 cas à pow(x, y, n), utilisé comme référence de vérification.

## Question 1b Compléter l’algorithme d’Euclide étendu

home_ext_euclide(y, b) cherche le nombre qui, multiplié par b, donne un reste de 1 modulo y. C’est ce que l’on appelle un inverse modulaire. Le module vient en premier dans l’appel ; le calcul de la clé privée d’Alice est donc home_ext_euclide(lambda_a, ea).

L’algorithme suit les divisions d’Euclide et le coefficient de b dans l’identité de Bézout. Si le PGCD vaut 1, ce coefficient fournit l’inverse recherché.

$$s × y + t × b = 1$$
$$t × b ≡ 1 (mod y)$$

Le résultat est ramené dans l’intervalle de 0 à y − 1. Lorsque le PGCD est différent de 1, la fonction signale qu’aucun inverse n’existe.

Avec le module 20 et le nombre 3, l’inverse vaut 7 : 3 × 7 = 21, qui laisse un reste de 1 modulo 20. La même méthode donne 2753 comme inverse de 17 modulo 3120 :

$$17 × 2753 = 15 × 3120 + 1$$

Dans le code de départ, phia et phib sont calculés avec un PPCM. J’ai utilisé les noms lambda_a et lambda_b pour les distinguer de l’indicatrice d’Euler φ(n). Pour Alice comme pour Bob, on vérifie que e × d donne un reste de 1 modulo λ(n).

<!-- page -->

# Partie 1 Échange et remplacement de MD5

## Question 2 Simuler l’échange entre Bob et Alice

Bob commence par représenter son texte avec un nombre. Le texte passe en octets UTF-8, puis en entier big-endian. Il chiffre cet entier avec la clé publique d’Alice, formée de na et ea. Alice utilise ensuite son exposant privé da pour retrouver l’entier et reconstruire le texte.

Pour la signature, ce sont les clés de Bob qui interviennent. Bob signe l’empreinte du texte avec db. Alice recalcule l’empreinte du message qu’elle a retrouvé et vérifie les signatures avec eb et nb. Le chiffrement sert donc à réserver la lecture à Alice ; la signature permet de vérifier le contenu avec la clé de Bob, à condition de disposer de sa véritable clé publique.

| Contrôle sur Bonjour Alice | Résultat |
| --- | --- |
| Longueur UTF-8 | 13 octets |
| Entier du message | 5263545046498671831490868372325 |
| Message après déchiffrement | Bonjour Alice |
| Vérification de la signature | Valide |

La longueur en octets accompagne l’envoi pour ne pas perdre les éventuels zéros au début. Les deux conversions ont été modifiées ensemble pour conserver aussi les accents. Le programme affiche aussi le chiffré et les signatures pour suivre l’échange.

## Question 3a Remplacer MD5 par SHA 256

L’empreinte est calculée par hashlib.sha256(message.encode("utf-8")).digest(). Le passage intermédiaire par binascii.b2a_uu a été retiré. SHA-256 produit 32 octets, contre 16 pour MD5.

Le module de Bob ne fait que 206 bits : une empreinte de 256 bits ne tient pas nécessairement dans une seule opération RSA. Pour garder les clés fournies sans réduire l’empreinte modulo nb, elle est divisée en deux blocs de 25 et 7 octets, signés séparément. Alice doit valider les deux blocs. Cette solution permet de faire l’exercice avec les clés du TP. Elle ne correspond pas à un schéma de signature RSA standard.

## Question 3b Déterminer la nouvelle limite du message

La contrainte du chiffrement reste m < na. Pour accepter tous les contenus de L octets, il faut que 256 puissance L − 1 soit inférieur à na. Le module d’Alice fait 203 bits : 25 octets, soit 200 bits, tiennent toujours ; 26 octets peuvent dépasser cette taille.

La limite retenue est donc de 25 octets UTF-8. Cela permet 25 caractères ASCII, mais seulement 12 caractères é suivis d’un caractère ASCII. Certains entiers codés sur 26 octets pourraient tenir, mais la règle uniforme les refuse.

Le code de départ limitait la saisie à 10 caractères. La limite de 25 octets vient de la taille du module d’Alice. Le remplacement de MD5 par SHA-256 ne change pas la capacité du module RSA. Les messages plus longs sont traités par blocs dans la partie 3.

<!-- page -->

# Partie 2 Simulation du canal auxiliaire

## Question 1 Compter et interpréter les multiplications conditionnelles

home_mod_expnoent_trace fait le même calcul qu’en partie 1, mais garde une trace des opérations. Chaque bit à 1 entraîne une multiplication supplémentaire. La fonction compte ces multiplications et note l’ordre des bits rencontrés ; elle compte les carrés à part.

Pour 3 puissance 13 modulo 17, le résultat est 12. La fonction compte trois multiplications conditionnelles et quatre carrés. Les bits sont rencontrés dans l’ordre 1, 0, 1, 1 ; leur lecture dans l’autre sens donne la représentation habituelle 1101.

Le nombre total de multiplications conditionnelles donne le poids de Hamming de l’exposant, c’est-à-dire son nombre de bits à 1. Il ne permet pas, à lui seul, de connaître leur position. Par exemple, les exposants 11 et 13 comportent chacun trois bits à 1 sur quatre bits.

Un observateur qui distingue les opérations de chaque tour peut en déduire davantage que ce simple total : la position des multiplications peut révéler les bits de l’exposant. Dans le TP, ces événements sont notés directement par le programme. Ils représentent ce que l’on pourrait chercher à observer ; aucune mesure physique de consommation ou de cache n’a été réalisée.

## Question 2 Bonus Comparer plusieurs messages

Les essais sur les entiers 1, 42, 513 et 123456789 donnent tous 85 multiplications conditionnelles et 198 carrés pour le déchiffrement direct avec la clé d’Alice. Ces nombres dépendent de l’exposant privé, qui ne change pas entre les messages.

Les temps sont mesurés avec perf_counter_ns sur cinq séries de trente calculs. Le tableau donne la médiane du temps moyen par opération, avec les paramètres CRT déjà préparés. Ces valeurs ont été obtenues sous Python 3.12.14 sur Linux ; elles peuvent changer d’une exécution à l’autre.

| Message entier | Direct en ns | CRT en ns |
| --- | --- | --- |
| 1 | 62661 | 43763 |
| 42 | 361520 | 182812 |
| 513 | 267391 | 246892 |
| 123456789 | 156573 | 112352 |

Le CRT est plus rapide dans cette série de mesures. Les durées restent sensibles à la machine, à sa charge et aux valeurs manipulées. Le cas du message 1 est notamment moins coûteux. Ces variations ne suffisent pas à déduire la clé privée à partir d’un simple chronométrage.

<!-- page -->

# Partie 2 Optimisation par le CRT

## Question 3a Calculer les exposants réduits

Au lieu de faire tout le déchiffrement modulo n, on fait deux calculs, l’un modulo p et l’autre modulo q. Ces nombres sont plus petits. Les exposants réduits sont préparés une fois, puis réutilisés :

$$dp = d mod (p − 1)$$
$$dq = d mod (q − 1)$$

L’inverse de q modulo p, noté q_inv, est obtenu avec la fonction d’Euclide étendu.

## Question 3b Reconstituer le message

Les résultats mp et mq ne sont pas deux morceaux du texte. Ce sont deux restes du même message : l’un modulo p, l’autre modulo q. Le CRT permet de retrouver le seul entier entre 0 et n − 1 qui respecte ces deux restes :

$$mp = cᵈᵖ mod p$$
$$mq = cᵈᑫ mod q$$
$$h = ((mp − mq) × q_inv) mod p$$
$$m = (mq + h × q) mod n$$

Dans l’exemple du TP, p = 137, q = 131, c = 8363 et d = 11787. Le programme obtient dp = 91, dq = 87 et q_inv = 114. Les résultats intermédiaires sont mp = 102 et mq = 120.

On trouve alors h = 3, puis m = 120 + 3 × 131 = 513. Le rechiffrement avec e = 3 redonne 8363. Le calcul CRT et le calcul direct restituent donc le même message.

Les tests couvrent également les deux clés du TP, avec des chiffrés pseudoaléatoires et les valeurs limites 0, 1, p, q et n − 1. Le cas d’un chiffré divisible par p ou q est traité explicitement, y compris lorsqu’un exposant réduit est nul.

## Question 3c Bonus Commenter le lien avec la surface d’attaque

Le CRT diminue le coût du calcul en travaillant sur des modules plus petits. Cela ne supprime pas les canaux auxiliaires : les calculs utilisent encore des exposants secrets, dp et dq. Une durée d’exécution plus courte ne suffit donc pas à conclure à une réduction générale de la surface d’attaque.

Le CRT peut aussi être sensible aux attaques par faute. Dans certains scénarios, un résultat erroné sur l’une des deux branches peut aider à retrouver un facteur du module. Des protections telles que l’aveuglement, la vérification du résultat et des primitives à temps constant restent nécessaires dans une implémentation réelle.

<!-- page -->

# Partie 3 Bourrage et traitement par blocs

## Question 1 Découper chiffrer et reconstituer le message

Le module d’Alice occupe 203 bits, soit k = 26 octets après arrondi. Le sujet impose j inférieur ou égal à k/2 ; chaque morceau du message contient donc au maximum 13 octets.

Le texte est encodé en UTF-8 puis découpé en octets. Pour chaque morceau, le programme génère k − j − 3 octets non nuls, regroupés dans PS, et construit le bloc suivant :

$$EM = 00 || 02 || PS || 00 || morceau$$

| Élément du bloc plein | Taille |
| --- | --- |
| Préfixe 00 02 | 2 octets |
| PS non nul | 10 octets |
| Séparateur 00 | 1 octet |
| Morceau du message | 13 octets |
| Bloc complet | 26 octets |

Les valeurs de PS sont tirées avec secrets.randbelow(255) + 1, donc entre 1 et 255, comme le domaine demandé par alea % 255 + 1. La longueur de PS est toujours d’au moins huit octets. Si le dernier morceau est plus court, PS est allongé pour conserver la taille du bloc.

Le bloc est converti en entier et chiffré avec la clé publique d’Alice. Son premier octet nul garantit ici une valeur inférieure au module. Au déchiffrement, to_bytes reconstruit exactement 26 octets afin de retrouver ce zéro initial.

Alice vérifie le préfixe, le séparateur et les tailles, puis enlève le bourrage. Elle réunit d’abord les octets et les décode seulement après, car un caractère UTF-8 peut être coupé entre deux blocs. La signature est vérifiée sur le texte complet retrouvé.

Le texte d’essai « Bonjour Alice ! Ce message dépasse vingt-cinq octets et contient des accents é et un emoji 😀. » occupe 98 octets et produit huit blocs. Le texte retrouvé est identique et la signature est valide. Le déchiffrement direct donne le même résultat que le CRT.

Le bourrage rend le chiffrement aléatoire : deux envois du même message donnent normalement des chiffrés différents. Ce format reste celui du TP, inspiré de PKCS#1 v1.5. Un service révélant la validité du bourrage pourrait servir de padding oracle. Le message d’erreur générique utilisé ici ne garantit pas un temps d’exécution constant.

<!-- page -->

# Partie 3 Certificat du site Springer

## Question 2a Identifier la clé publique

Le certificat présenté par link.springer.com a été relevé le 16 octobre 2026 à 16:02:25 UTC, avec vérification de la chaîne et du nom d’hôte. Son sujet est CN=*.springer.com. Il contient une clé publique RSA de 2048 bits, avec l’exposant 65537, soit 0x10001.

Le certificat relevé est conservé dans le dépôt pour pouvoir retrouver les valeurs étudiées, même après son renouvellement.

## Question 2b Identifier la fonction d’empreinte

L’algorithme de signature du certificat est sha256WithRSAEncryption, d’OID 1.2.840.113549.1.1.11. Le hash utilisé dans cette signature est donc SHA-256.

L’empreinte SHA-256 du certificat complet, calculée séparément pour identifier le fichier observé, vaut :

```text
27d5c26b2047ca2b459030694a9fed4e68157c22b802be2ffb231ee09d327350
```

## Question 2c Identifier le bourrage

La signature du certificat utilise RSASSA-PKCS1-v1_5. Cet encodage concerne la signature produite par l’autorité émettrice. Ce n’est pas le bloc de chiffrement 00 02 utilisé dans la partie précédente.

| Autre champ observé | Valeur |
| --- | --- |
| Autorité émettrice | Let's Encrypt, YR2 |
| Début de validité UTC | 23 septembre 2026 à 11:18:57 |
| Fin de validité UTC | 22 décembre 2026 à 11:18:56 |
| Version TLS négociée | TLS 1.3 |
| Suite négociée | TLS_AES_128_GCM_SHA256 |

La présence d’une clé RSA dans le certificat ne signifie pas que le trafic est chiffré directement par RSA. La connexion observée utilise AES-GCM pour protéger les données et TLS 1.3 ne reprend pas l’ancien échange de clés RSA. Le schéma de signature de CertificateVerify ne peut pas être déduit du seul certificat.

Les valeurs ci-dessus décrivent le certificat au moment du relevé. Elles pourront changer lors de son renouvellement ou selon la négociation du client.

<!-- page -->

# Vérifications avec de petits exemples

Pour vérifier les calculs à la main, on peut reprendre les mêmes fonctions avec de petits nombres. Voici quelques exemples.

## Retrouver un message avec de petites clés

On prend p = 11 et q = 5, donc n = 55 et λ(n) = 20. On choisit e = 3 et d = 7 : ces exposants vont ensemble, car 3 × 7 laisse un reste de 1 modulo 20. Pour ce seul exemple, le message est directement l’entier 8, sans texte ni bourrage.

$$Chiffrement : 8³ mod 55 = 17$$
$$Déchiffrement : 17⁷ mod 55 = 8$$

On retrouve donc bien 8. Dans le programme principal, le principe est le même, mais le texte est d’abord converti en entier et les clés sont celles de l’énoncé.

## Vérifier le même calcul avec le CRT

Pour ce chiffré 17, on trouve dp = 7, dq = 3 et q_inv = 9. Les deux calculs donnent mp = 8 et mq = 3. La recombinaison donne h = 1, puis m = 3 + 1 × 5 = 8. Le calcul direct et le CRT arrivent bien au même résultat.

## Changer une seule lettre dans le message

Les textes Bonjour et bonjour ne diffèrent que par la majuscule. Leurs empreintes SHA-256 sont pourtant différentes. Voici leurs seize premiers caractères hexadécimaux ; les empreintes complètes restent de 32 octets.

| Texte | Début du SHA-256 |
| --- | --- |
| Bonjour | 9172e8eec99f144f |
| bonjour | 2cb4b1431b84ec15 |

## Vérifier le découpage en blocs

Les 26 lettres ABCDEFGHIJKLMNOPQRSTUVWXYZ occupent 26 octets en UTF-8. Avec 13 octets par morceau, on obtient deux blocs : ABCDEFGHIJKLM puis NOPQRSTUVWXYZ. Après déchiffrement et retrait du bourrage, leur réunion restitue l’alphabet complet.

Un accent illustre pourquoi le décodage attend la fin : douze lettres A suivies de é occupent 14 octets. Les deux octets de é, C3 et A9 en hexadécimal, se retrouvent de part et d’autre de la coupure à 13 octets. Réunir les octets avant de décoder permet de retrouver la lettre.

<!-- page -->

# Lancer les trois parties

Les deux fichiers Walter_Arthur_main.py et Walter_Arthur_util.py doivent être placés dans le même dossier. Le premier lance les exemples ; le second contient les fonctions de calcul. Python 3.10 ou plus récent suffit, sans bibliothèque supplémentaire à installer.

## Partie 1 Échange entre Bob et Alice

```powershell
python Walter_Arthur_main.py --partie 1 --message "Bonjour Alice"
```

Le programme chiffre le message pour Alice, le déchiffre et vérifie la signature de Bob. Le texte retrouvé doit être identique au texte envoyé, avec signature_valide à true. Cette partie accepte au maximum 25 octets UTF-8.

## Partie 2 Traces et calcul CRT

```powershell
python Walter_Arthur_main.py --partie 2
```

Cette partie utilise les nombres des exemples du TP. Elle affiche les multiplications comptées, la recombinaison CRT et la comparaison des temps. Il n’y a pas de message à saisir.

## Partie 3 Message long avec bourrage

```powershell
python Walter_Arthur_main.py --partie 3 --message "Un message long avec des accents é."
```

Le texte est découpé en blocs, puis reconstitué après déchiffrement. Le programme vérifie aussi que le CRT donne le même texte que le calcul direct. Les chiffrés varient car le bourrage est aléatoire.

## Enchaîner les trois parties

```powershell
python Walter_Arthur_main.py --partie toutes --message "Bonjour Alice"
```

L’option toutes lance les trois démonstrations avec le même message. Comme elle inclut la partie 1, sa limite reste de 25 octets UTF-8. Pour un texte plus long, il faut choisir uniquement la partie 3. Sans --message, le programme demande le texte dans le terminal, sauf pour la partie 2.

Ces vérifications montrent que le programme retrouve les messages attendus. Elles ne rendent pas l’échange utilisable en pratique : les clés sont petites, la signature en deux blocs est une adaptation au TP et les calculs Python ne sont pas à temps constant.
