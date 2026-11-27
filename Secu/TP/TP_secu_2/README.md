# TP 2 · Blockchain

## Ce qu’il faut rendre

Le devoir Teams du vendredi 27 novembre 2026 fixe l’échéance à 20 h 30. Il demande deux fichiers Python. Le premier reprend le carnet personnel de `main.py`. Le second contient le registre entre amis et sert de support à la présentation. Chaque fichier peut être lancé séparément.

| Fichier | Contenu | Remise |
| --- | --- | --- |
| [Partie1_Walter_Arthur.py](Partie1_Walter_Arthur.py) | Réponses Q1 à Q6, six écritures du sujet, signatures et mesure du minage | Individuelle |
| [Partie2_Walter.py](Partie2_Walter.py) | Q7 et Q8, démonstration et menu pour utiliser le registre | Nom retenu avec un seul nom de famille. En binôme ou trinôme, chaque membre remet le même code sous un nom de fichier qui reprend les noms du groupe. |

## Exécution

Depuis ce dossier, avec Python 3.10 ou plus récent, installer la dépendance puis lancer les deux parties. Sous Windows, si le lanceur `py` est absent, utiliser `python` à sa place.

```powershell
py -3 -m pip install ecdsa==0.19.1
py -3 Partie1_Walter_Arthur.py
py -3 Partie2_Walter.py
```

Le lancement normal de la première partie est court. La mesure de dix minutes se demande explicitement. Pour la seconde partie, le lancement normal joue l’exemple du billet de train et du déjeuner. Le menu ouvre un carnet vide.

```powershell
py -3 Partie1_Walter_Arthur.py --mesure 600
py -3 Partie2_Walter.py --menu
py -3 -m unittest discover -s . -p "test_*.py" -v
```

## Lecture de l’énoncé et du programme fourni

La première page du sujet décrit un bloc avec cinq éléments. Son empreinte est calculée à partir des quatre premiers. L’empreinte finale elle-même reste en dehors du calcul, sinon sa définition serait circulaire.

| Élément décrit par le sujet | Ce que fait le fichier fourni | Choix pour le TP |
| --- | --- | --- |
| Empreinte du bloc précédent | `previous_block_hash` reprend celle du dernier bloc. La genèse utilise le texte `"0"`. | Conserver ce lien dans les deux parties. |
| Donnée du bloc | `transaction_list` est une liste de libellés. `block_data` les assemble avec l’empreinte précédente. | Garder les six libellés en Q4. Introduire des champs distincts pour pouvoir calculer les dettes en Q7. |
| Signature | L’import ECDSA figure déjà dans le fichier. Aucune clé et aucune signature ne sont utilisées. | Signer le libellé en partie 1. Demander l’accord de chaque personne concernée en partie 2. |
| Preuve de travail | Le SHA-256 est calculé une seule fois. Le bloc est accepté quel que soit son préfixe. | Ajouter un compteur entier, le nonce. Modifier le compteur jusqu’à obtenir le nombre de zéros demandé. |
| Empreinte du bloc | `block_hash` est le SHA-256 de `block_data` encodé en UTF-8. | Couvrir aussi les signatures et le nonce. Garder une représentation identique à chaque recalcul. |

## Partie 1 · Tenir ses propres comptes

| Question | Réponse à pouvoir expliquer | Où l’observer |
| --- | --- | --- |
| Q1 | La priorité est l’intégrité. Si une écriture change, son empreinte recalculée change. Le lien conservé par son successeur permet de repérer l’écart. | Commentaire Q1, puis les empreintes affichées à l’exécution. |
| Q2 | La chaîne de départ contient une genèse puis six blocs. Le premier salaire est déjà une transaction distincte de la genèse. | Commentaire Q2 et les six libellés `t1` à `t6`. |
| Q3 | À l’origine, le programme accepte tout libellé, calcule une empreinte et l’affiche. Le modèle du sujet ajoute le contrôle des fonds, les signatures, le minage et la vérification collective. | Commentaire Q3. |
| Q4 | Une clé privée ECDSA P-384 signe les octets UTF-8 de chaque libellé avec SHA-256. La clé publique vérifie la signature avant l’ajout du bloc. | Les deux dernières lignes du lancement court comparent la dépense de 70 € et le même texte porté à 700 € avec la signature initiale. |
| Q5 | La signature du titulaire atteste son accord pour inscrire le salaire. L’employeur n’a fourni aucun justificatif signé. Même une chaîne entièrement cohérente peut donc donner un solde de départ faux. | Commentaire Q5 et libellé du premier versement. |
| Q6 | Pour mesurer ce que le PC peut atteindre, fixer la durée, garder un même bloc signé et parcourir les nonces. Retenir la meilleure empreinte réellement obtenue. | `mesurer_minage`, option `--mesure 600` et résultats ci-dessous. |

### Interpréter la mesure de Q6

Le préfixe fixe encode le hash précédent, la liste des opérations et les signatures. Le programme ajoute un séparateur et le nonce décimal avant d’appeler SHA-256. À chaque nouveau record, il affiche le nombre de zéros en tête, le nonce et le temps écoulé. En fin de mesure, il affiche aussi le nombre d’essais et l’empreinte complète. La lecture de l’horloge se fait par séries de 4 096 essais.

**Résultat du 27 novembre 2026 sur le Core i5-12400F, sous Windows et Python 3.12.14.** Le programme a testé 298 602 496 nonces sur le premier bloc signé en 600,01 s, soit 497 664 essais/s. Le meilleur résultat est de **six zéros hexadécimaux**.

| Préfixe recherché | Premier nonce trouvé | Temps écoulé |
| --- | ---: | ---: |
| 4 zéros | 33 952 | 0,07 s |
| 5 zéros | 371 144 | 1,70 s |
| 6 zéros | 26 361 962 | 59,06 s |
| 7 zéros | Aucun sur cette série | 600,01 s de recherche |

Empreinte du meilleur essai : `000000ce3ec1c6b558fb64d2137f8fab837e2135c241f7f628126c20f3f6983e`. Au débit mesuré, le temps **moyen** attendu pour sept zéros est d’environ neuf minutes. Le tirage de ce soir illustre qu’une recherche de dix minutes peut finir sans en trouver.

Il y a seize valeurs possibles pour un chiffre hexadécimal. Obtenir six zéros demande en moyenne 16 777 216 essais. Pour sept zéros, la moyenne passe à 268 435 456 essais. Le seuil de vingt zéros cité dans l’introduction représente 80 bits imposés, soit environ 1,21 × 10²⁴ essais en moyenne. Les blocs ordinaires utilisent deux zéros pour que la démonstration reste fluide.

Une mesure donne un résultat atteint dans des conditions précises. Un nouvel essai crée une nouvelle paire de clés et donc une autre signature. Les nonces gagnants et le meilleur nombre de zéros peuvent changer sur la même machine.

## Partie 2 · Comptes entre trois amis

Le registre répond à la question « qui doit combien à qui ? ». Les trois amis démarrent quittes. Une avance crée une dette, un remboursement la réduit et un achat partagé crée une dette envers la personne qui a payé. Le programme ignore les soldes des comptes bancaires réels.

| Opération | Exemple | Signatures attendues | Effet sur les dettes |
| --- | --- | --- | --- |
| Avance | Alice avance 20 € à Benoît pour un billet. | Alice et Benoît | Benoît doit 20 € à Alice. |
| Achat | Chloé règle un déjeuner de 30 € pour les trois. | Alice, Benoît et Chloé | Alice et Benoît doivent chacun 10 € à Chloé. Chloé assume sa propre part. |
| Remboursement | Benoît rend 8 € à Alice. | Benoît et Alice | Sa dette envers Alice descend à 12 €. Les dettes du déjeuner restent inchangées. |

### Enregistrer et valider une opération

1. Le payeur indique le type, les bénéficiaires, le montant total et le motif. Le menu inscrit la date avec son fuseau horaire. Le programme convertit le montant en centimes entiers. Une saisie comme `12,50` vaut exactement 1 250 centimes.
2. L’opération est affichée avant les accords. Chaque participant valide ou refuse à son tour sur le même poste. Un seul refus annule l’ajout. Pour un achat, on sélectionne aussi le payeur parmi les personnes qui partagent la dépense.
3. Chaque signature couvre la date, le type, le payeur, les bénéficiaires, le montant, le motif et la référence du bloc précédent. Lier l’accord à cette référence évite qu’une signature déjà utilisée autorise une deuxième inscription à la fin du carnet.
4. Avant de miner, le registre vérifie les accords à partir des clés publiques et contrôle la règle du remboursement. Un remboursement de 21 € sur une dette de 20 € est refusé. On peut saisir une nouvelle avance si l’on veut réellement prêter la différence.
5. Le bloc est ajouté après la preuve de travail. L’option de validation de Q8 repart de la genèse, contrôle les liens, recalcule chaque empreinte, vérifie le préfixe requis, les signatures et les règles de solde. Une erreur indique le premier bloc en cause.

La convention interne est `soldes[A][B] > 0` quand B doit de l’argent à A. Chaque mouvement entre deux personnes a deux écritures de signes opposés. Pour un achat de 10 € à trois, la répartition est de 3,34 €, 3,33 € et 3,33 €. L’ordre alphabétique départage les centimes restants, ce qui donne le même résultat à chaque relecture. L’historique affiche les opérations auxquelles l’ami a participé, dans l’ordre des blocs.

### Préparer la présentation

Lancer `Partie2_Walter.py`. À la fin de l’exemple, trois dettes restent ouvertes.

| Qui doit payer ? | À qui ? | Montant restant |
| --- | --- | ---: |
| Benoît | Alice | 12,00 € |
| Alice | Chloé | 10,00 € |
| Benoît | Chloé | 10,00 € |

Le programme affiche les deux relations d’Alice puis l’historique de Chloé. Chloé y retrouve uniquement le déjeuner. Pour montrer le rôle des signatures en direct, ouvrir `--menu`, proposer une avance et refuser au nom du deuxième ami. Demander ensuite la validation de la chaîne. Le compteur indique toujours zéro opération. Refaire l’avance avec les deux accords, puis consulter le solde de chaque ami.

Le menu simule trois personnes devant un seul poste. Les clés sont générées en mémoire au démarrage et le carnet dure le temps de la session. Dans cet exercice, la vérification repose sur le registre des clés publiques créé au départ. La chaîne locale ne dispose d’aucune copie indépendante pour prouver qu’un dernier bloc a disparu.

## Vérifications

Les 14 tests de [test_blockchain.py](test_blockchain.py) ont réussi sous Python 3.11.4 et 3.12.10. Ils portent sur les signatures, le contenu daté, le lien au bloc précédent, la preuve de travail, le refus d’un participant, le remboursement intégral ou excessif, le partage au centime et le filtre d’historique. Ils recalculent également la preuve annoncée par une mesure courte de Q6 et exercent le menu depuis la proposition d’une avance jusqu’à l’affichage du solde.

Lors d’un contrôle séparé, OpenSSL a vérifié les trois signatures produites par le programme sur le même achat de groupe. La seule dépendance à installer pour faire fonctionner les deux fichiers du devoir reste `ecdsa` et ce que `pip` installe avec elle.

La [documentation de python-ecdsa](https://ecdsa.readthedocs.io/en/latest/quickstart.html) décrit la génération de la paire de clés, la signature déterministe et sa vérification.
