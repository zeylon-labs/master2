# TP LUSS01 · Du serveur HTTP au club privé en HTTPS

Les parties 1 à 5 s’exécutent sous Windows avec Python 3.12.10. Ouvrir PowerShell dans le dossier qui contient `run_server.py`. Le PDF individuel du lot Teams contient les identifiants fictifs du jeu remis et les captures commentées.

## Installer et tester

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Versions directes testées : Flask 3.1.3, Werkzeug 3.1.9, cryptography 50.0.2 et pem 23.1.0. Les tests génèrent des jeux temporaires et ouvrent des ports éphémères sur la boucle locale.

## Partie 1 · HTTP sur le port 8081

```powershell
.\.venv\Scripts\python.exe run_server.py http
```

Ouvrir `http://localhost:8081/`. Le serveur renvoie le mot de démonstration affiché sur la page. Pour l’observer dans Wireshark sous Windows, sélectionner **Adapter for loopback traffic capture** (Npcap), appliquer le filtre de capture `tcp port 8081`, lancer la capture, puis actualiser la page. Arrêter la capture. Appliquer le filtre d’affichage `tcp.port == 8081 && http.response.code == 200`, sélectionner la réponse, puis suivre le flux TCP pour lire le corps HTML. Si nécessaire, associer le port 8081 à HTTP dans **Analyser → Décoder comme**. Arrêter le serveur avec **Ctrl+C**.

## Parties 2 et 3 · Construire ou lire les certificats

**Première exécution depuis Git.** Choisir deux mots de passe fictifs différents pour les clés. Le premier protège la clé de l’autorité de certification (CA), le second celle du serveur.

```powershell
.\.venv\Scripts\python.exe build.py
.\.venv\Scripts\python.exe print_pems.py
```

`build.py` crée cinq fichiers dans `resources`. La CA signe sa propre identité, puis signe la demande de certificat (CSR) du serveur pour le nom DNS `localhost`. Pour créer un jeu indépendant, utiliser `build.py --resources .\autre-jeu`. Le même argument est disponible pour la lecture, la création du compte et le lancement.

**Depuis le ZIP Teams.** Les cinq PEM et le compte sont fournis dans `resources`. Lancer directement `print_pems.py`, puis le serveur HTTPS. Les numéros de série et les empreintes SHA-256 permettent de retrouver le jeu représenté dans le rapport.

## Parties 4 et 5 · Connexion d’un membre

Depuis Git, créer le compte local une fois. Saisir le mot de passe du compte puis le message mensuel à transmettre au membre.

```powershell
.\.venv\Scripts\python.exe run_server.py creer-compte --identifiant membre
```

Lancer le service final et déverrouiller la clé du serveur à l’invite.

```powershell
.\.venv\Scripts\python.exe run_server.py
```

Ouvrir `https://localhost:8443/`. Un profil vierge signale que la CA locale est inconnue. Pour une session de test, importer **seulement le certificat public** `resources/ca-public-key.pem` parmi les autorités de confiance d’un profil de navigateur dédié, après vérification de son empreinte. Recharger la page, saisir l’identifiant et le mot de passe du compte. Pour vérifier la chaîne et le nom avec Python depuis un deuxième PowerShell dans le même dossier, exécuter la commande ci-dessous. Le serveur répond **401** au client anonyme après la négociation TLS.

```powershell
.\.venv\Scripts\python.exe -c "import http.client,ssl; c=http.client.HTTPSConnection('localhost',8443,context=ssl.create_default_context(cafile='resources/ca-public-key.pem')); c.request('GET','/'); print(c.getresponse().status); c.close()"
```

Le fichier local `resources/compte.json` conserve l’identifiant, le message à distribuer et l’empreinte salée du mot de passe du compte. Werkzeug vérifie le mot de passe avec scrypt (`N=32768, r=8, p=3`). La session signée contient l’identifiant. Une déconnexion efface le cookie du navigateur et le redémarrage invalide les sessions précédentes. Arrêter le serveur avec **Ctrl+C**.

Pour un rejeu automatisé, les variables de processus `TP_CA_MDP`, `TP_SERVEUR_MDP`, `TP_COMPTE_MDP` et `TP_MESSAGE` remplacent les saisies correspondantes. Le rapport et le ZIP de remise sont locaux. Les sources fournies par l’enseignant se trouvent dans le dossier `sources` du dépôt.
