# Mandat Codex — TP LUSS01 · Du serveur HTTP au club privé en HTTPS

Travaille dans le dépôt `zeylon-labs/master2`, sous `Secu/TP/TP_secu_3/`. Développe les parties 1 à 5 sur le PC Windows, teste-les, prépare le rendu Teams et publie le travail versionnable sur `origin/main` après vérification. Fais ces étapes en une seule session si le poste le permet.

**Échéance communiquée par Arthur** — jeudi 3 décembre 2026, soit cinq jours après le 28 novembre. L’heure limite reste à confirmer sur Teams. La mention de juin page 1 correspond à l’ancien calendrier. Préparer le rapport individuel au nom d’Arthur Walter. Si un binôme est confirmé, reprendre les deux noms dans le PDF.

## Sources et état de départ

- Lire [l’énoncé de quatre pages](sources/LUSS01_https.pdf) et partir des [six fichiers Python d’origine](sources/codes.zip). Sur le PC d’Arthur, le dépôt est dans `C:\dev\master2`. La copie déjà extraite se trouve sous `Secu\TP\TP_secu_3\codes\codes\`. Les six fichiers correspondent octet pour octet à l’archive.
- L’archive contient `build.py`, `run_server.py`, `print_pems.py`, `ca/core.py`, `server/core.py`, `tools/core.py` et un dossier `resources/` vide. Garder le PDF et le ZIP intacts. Travailler dans une arborescence exécutable qui conserve les imports du squelette. Les noms utilisés dans le texte du sujet, `print_pem.py` et `run_serveur.py`, désignent les fichiers livrés `print_pems.py` et `run_server.py`.
- `tools/core.py` fournit déjà la génération RSA 2048, les clés privées chiffrées, le certificat autosigné, la CSR et sa signature. `ca/core.py`, `server/core.py` et `build.py` contiennent les appels à compléter. `sign_csr()` écrit le certificat sur disque et ne renvoie actuellement aucun objet. Vérifier le fichier produit. Dans `print_pems.py`, la représentation d’une liste d’objets PEM peut être trop sommaire pour le rapport. Afficher les champs X.509 des deux certificats en plus de leur identification PEM.
- `run_server.py` sert déjà le message en HTTP sur le port 8081. Il manque le mode HTTPS et le compte utilisateur. Les dépendances du sujet sont Flask, cryptography et pem. Donner les commandes PowerShell réellement utilisées depuis un environnement Python propre et les versions testées.

## Travail et preuves attendues

| Partie du sujet | Travail à réaliser | Preuve à insérer dans le rapport |
| --- | --- | --- |
| 1 · HTTP, p. 3 | Remplacer `hypsilophodon` par un mot de passe de club fictif. Démarrer le serveur sur la boucle locale, afficher `http://localhost:8081/`, puis arrêter le serveur. Garder un moyen de rejouer cette démonstration indépendamment de la version finale. | Deux captures réelles commentées. La première montre l’URL et le message dans le navigateur. La seconde montre ce même texte dans le corps de la réponse HTTP de **ce serveur de TP**, sur la boucle locale de Wireshark, pour le port 8081. |
| 2 · Autorité de certification, p. 3 | Compléter `CertificateAuthority` et `build.py`. Générer `ca-private-key.pem` chiffré et `ca-public-key.pem`, certificat autosigné de la CA. | Visualisation du certificat effectivement généré, identité choisie pour la CA (pays, région, ville, organisation, nom commun), mot de passe de démonstration permettant d’ouvrir la clé privée de la CA. Expliquer comment reconnaître l’autorité dans le certificat. |
| 3 · Serveur et signature, p. 3 | Compléter `Server`, `get_csr()` si nécessaire, la signature côté CA et l’orchestration. Générer `server-private-key.pem` chiffré, `server-csr.pem` puis `server-public-key.pem`, certificat du serveur signé par la CA. | Visualisation du certificat serveur effectivement généré, mot de passe de sa clé privée et courte explication de la différence entre la demande de signature et le certificat délivré. Identifier le sujet, l’émetteur et le nom DNS couvert. |
| 4 · HTTPS, p. 3 | Charger le certificat du serveur et sa clé chiffrée dans le serveur Flask. Tester `https://localhost` sur le port documenté. Le squelette prévoit une liste de noms alternatifs vide. Ajouter `localhost` au SAN DNS et vérifier qu’il est repris dans le certificat final. | Capturer l’avertissement réel d’un navigateur qui ne connaît pas la CA, puis la lecture du message du club en HTTPS. Commenter le motif effectivement affiché. Expliquer deux solutions sûres. Décrire comment fournir la CA à un client de test ou aux postes administrés par le club, et comment obtenir, pour un vrai domaine, un certificat d’une autorité reconnue. |
| 5 · Compte utilisateur, p. 4 | Créer au moins un compte avec identifiant et mot de passe. Protéger l’accès au message final. Distinguer le mot de passe du compte, le message mensuel du club et les deux mots de passe des clés PEM. | Montrer que la connexion valide donne accès au message et que l’accès anonyme ou avec un mauvais mot de passe échoue. Expliquer le traitement du mot de passe utilisateur, explicitement noté dans le sujet. |

**Choix de réalisation.** Un formulaire de connexion, une session Flask et un seul compte local suffisent pour la partie 5. Conserver un hachage salé et paramétré du mot de passe du compte, par exemple avec scrypt via Werkzeug. Documenter la création du compte et la vérification du hachage. Utiliser des données fictives. Le membre authentifié doit pouvoir lire le message après un démarrage normal du serveur. Pour la partie 4, utiliser le certificat correspondant à l’URL exacte. Pour reproduire les deux états de confiance, privilégier un profil de navigateur dédié ou une configuration de test isolée. Conserver la vérification TLS active dans le test de succès.

**Partie 6, p. 4.** L’extension est facultative et signalée « Projet à 3 ». Les deux pistes proposées sont les principes OWASP appliqués à plusieurs utilisateurs ou le chiffrement ABE selon leur statut. Avec le périmètre individuel ou en binôme, terminer le mandat à la partie 5.

## Ordre de réalisation et recette

Commencer par vérifier Python, les dépendances, le navigateur, Wireshark et la capture locale Npcap sous Windows. Prendre les deux captures HTTP avant de passer au serveur final. Si l’accès à la boucle locale ou à une fenêtre graphique manque, poursuivre le développement, les tests réseau et la rédaction. À la fin, indiquer exactement la capture manquante et le geste restant sur le poste. Un journal réseau peut aider au diagnostic. La pièce demandée en partie 1 est une capture d’écran Wireshark.

| Contrôle à exécuter | Critère de réussite |
| --- | --- |
| Relancer depuis des ressources vierges | Le script de construction crée les cinq PEM aux noms attendus. Un deuxième essai dans un autre dossier temporaire produit un jeu cohérent, sans écraser les pièces choisies pour le rendu. |
| Ouvrir les clés et lire les certificats | Chaque clé s’ouvre avec son propre mot de passe et échoue avec un mot de passe erroné. Le certificat de la CA est autosigné et porte la contrainte CA. Les certificats sont dans leur période de validité au moment du test. |
| Contrôler la CSR et la signature | Vérifier la signature de la CSR, la concordance de sa clé publique avec la clé du serveur et le certificat final, puis la signature du certificat serveur par la CA. Vérifier le SAN DNS `localhost`. |
| Exercer le serveur depuis un vrai client réseau | En HTTP de démonstration, le client reçoit le message attendu. En HTTPS, le client qui ne connaît pas la CA refuse le certificat. Avec le certificat CA fourni explicitement comme racine et le contrôle du nom activé, la connexion à `localhost` réussit. Un nom non couvert échoue à la vérification du nom. Relever l’erreur réelle de chaque cas. |
| Exercer l’authentification sur le service final | Vérifier l’accès direct anonyme, la tentative avec un mot de passe erroné et la connexion avec le bon compte. Le secret du club est absent des réponses refusées et présent après authentification. Vérifier le stockage du hachage et, si une déconnexion est fournie, la perte d’accès après celle-ci. |
| Rejouer le rendu dans un dossier propre | Extraire une copie du lot destiné à Teams, installer les dépendances documentées, suivre les commandes de lancement et vérifier que les cinq PEM remis correspondent aux deux visualisations du PDF. Ouvrir le PDF, contrôler la lisibilité des captures et leur légende. Arrêter les serveurs de test. |

Pour chaque contrôle, conserver la commande ou le geste, le résultat attendu, le résultat observé et le verdict. Corriger et rejouer les contrôles qui échouent. Utiliser des tests automatisés pour la génération des fichiers, la validation TLS et les décisions d’accès. Les captures du navigateur et de Wireshark doivent provenir du TP exécuté sur le poste. En cas de blocage graphique, livrer un rapport marqué provisoire, avec les preuves manquantes clairement identifiées.

## Rendu Teams et publication Git

1. Rédiger un rapport PDF en français, organisé en cinq parties, avec un court commentaire par preuve. Pour un rendu individuel, utiliser `Walter_Arthur.pdf`. Y inscrire les deux mots de passe fictifs de déchiffrement des clés exigés par le sujet. Joindre **tous les fichiers Python du projet** et **les cinq PEM du même jeu**. Ajouter les indications minimales de lancement, de création du compte de test et de connexion. Préparer le lot localement pour remise par Arthur.
2. Versionner les sources de développement, les tests, les dépendances et le mode d’emploi dans le dossier du TP. Conserver localement le lot de remise, les clés privées et le PDF qui donne leurs mots de passe. Le dépôt doit permettre de régénérer un jeu de démonstration indépendant. Contrôler les fichiers du commit, notamment les captures, la configuration locale et les éventuels mots de passe.
3. Partir de `origin/main` à jour, préserver les travaux locaux existants, puis intégrer et pousser les changements vérifiés sur `main` selon le fonctionnement du dépôt. Vérifier le SHA distant et la présence des fichiers. Si une capture reste à faire, décrire ce qui est publiable et ce qui manque au rendu.
4. Restituer à Arthur le chemin du PDF et du lot Teams, les commandes pour rejouer le TP, le bilan réel des tests et des captures, ainsi que le lien du commit distant. Distinguer « prêt à déposer » de « preuves restantes ». La remise sur Teams reste à Arthur.

### Références techniques

- [OWASP — stockage des mots de passe](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [Python — chargement d’un certificat et de sa clé privée par SSLContext](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_cert_chain)
- [Wireshark — capture sur la boucle locale Windows avec Npcap](https://wiki.wireshark.org/capturesetup/loopback)
