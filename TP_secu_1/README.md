# TP Sécurité 1 RSA

Trois parties implémentées, avec explications dans [le rapport](docs/Walter_Arthur_rapport.md).

- [Rapport PDF](docs/Walter_Arthur.pdf)
- [Rapport Word](docs/Walter_Arthur.docx)
- [Programme principal](Walter_Arthur_main.py) et [fonctions](Walter_Arthur_util.py)
- [Tests](tests/test_rsa.py) et [résultats réels](resultats/)

## Démarrer dans VS Code

Installer Python 3.10+ et l'extension Python de Microsoft. Ouvrir **ce dossier** dans
VS Code puis `Ctrl+Maj+P` > `Python: Select Interpreter`.
Les profils F5 sont fournis dans `.vscode/launch.json`.

```powershell
python Walter_Arthur_main.py --test
python Walter_Arthur_main.py --partie toutes --message "Bonjour Alice"
python Walter_Arthur_main.py --partie 3 --message "Un message long avec des accents é et un emoji 😀, qui dépasse vingt-cinq octets."
```

Sans `--message`, saisir le secret dans le terminal. Avec `--sortie chemin.json`,
enregistrer aussi les résultats. `--partie toutes` inclut la partie 1 et conserve
sa limite de **25 octets UTF-8**. Utiliser `--partie 3` pour un texte plus long.
Le programme de calcul et ses quinze tests n'ont aucune dépendance externe.

## Refaire le relevé du certificat

```powershell
python -m pip install -r requirements-certificat.txt
python outils/test_certificat.py
python outils/observer_certificat.py --sortie resultats/certificat_springer.json
```

La connexion vérifie la chaîne et le nom d'hôte. L'outil produit le PEM et le JSON.
Un échec réseau est enregistré comme un échec, jamais comme une observation.
Le relevé livré date du **16 octobre 2026 à 16:02:25 UTC**, via GitHub Actions.
Certificat observé : `CN=*.springer.com`, clé RSA 2048 bits, e=65537,
signature du certificat SHA-256 / RSASSA-PKCS1-v1_5. TLS 1.3 est distinct de
la signature du certificat et n'effectue pas l'ancien échange de clés RSA.

## Organisation des réponses

| Partie | Réalisation |
| --- | --- |
| 1 | Exponentiation rapide, Euclide étendu, échange, SHA-256 et limites |
| 2 | Traces conditionnelles, CRT, exemple officiel 513, bonus temporel et discussion |
| 3 | Découpage UTF-8, bourrage 00 02, débourrage, certificat daté |

Les signatures SHA-256 sont réparties en deux blocs (25 et 7 octets) pour
conserver les clés fournies. Ce choix explicite n'est pas RSA-PSS.
Le message est découpé en morceaux de 13 octets, bourrés à 26 octets.

## Régénérer le Word

```powershell
python -m pip install python-docx
python outils/generer_rapport.py
```

Le Markdown est la source du rapport. Le script produit le DOCX. Pour le PDF,
ouvrir le DOCX dans Word puis exporter en PDF, ou utiliser LibreOffice.

## Remise

Le sujet demande `Walter_Arthur_main.py`, `Walter_Arthur_util.py` et un PDF.
Les deux fichiers Python doivent rester dans le même dossier. Le rapport fourni
est `docs/Walter_Arthur.pdf`. Relire les réponses et reproduire les commandes
pour pouvoir expliquer le travail avant le dépôt individuel sur Teams.

Implémentation pédagogique uniquement : petites clés, signature non standard,
pas d'OAEP/PSS et pas de garantie de temps constant.
