# Atelier Cloud

Application pédagogique avec douze modules pour comprendre le cours Cloud et traitements distribués, réviser l’examen et préparer les TP.

## Utilisation

Sous Windows, double-cliquer sur `../../lancer_atelier_cloud.bat` pour ouvrir http://127.0.0.1:8765/. Le serveur démarre en arrière-plan et le second lancement le réutilise. Pour arrêter : `../../lancer_atelier_cloud.bat -Arreter`. On peut aussi ouvrir `index.html` dans un navigateur. Les interactions et les calculs fonctionnent localement, sans installation. La police distante est facultative : une police système est utilisée hors ligne.

Pour un aperçu avec un serveur local, depuis ce dossier :

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Puis ouvrir http://127.0.0.1:8765.

## Modules

- Saturation : utilisation de 0 à 100 %, traitement moyen de 5 à 50 ms, temps de réponse et attente du modèle M/M/1. À 100 %, le régime stationnaire n’est plus stable.
- Données distribuées : comparaison de la réplication et du partitionnement, panne du nœud A, lectures et propagation manuelle d’une mise à jour.
- Chord : recherche d’une clé de 0 à 31 parmi les neuf nœuds du support, avec les raccourcis et le chemin parcouru.
- ASP et cloud : accès web ou client natif, puis comparaison pédagogique des responsabilités sur site, IaaS, PaaS et SaaS.
- Événements et espace partagé : deux schémas interactifs, diffusion vers les abonnés présents, reprise d’une opération Linda et buffer de deux places à jetons. Accès direct : `index.html#evenements`.
- Architectures des systèmes : cinq schémas sur un même exemple (fiche du livre 42 et commande), parcours des échanges, déploiement illustratif et tableau de comparaison. Accès direct : `index.html#architectures`.
- Middleware : schéma des applications, des instances de middleware, des OS locaux et du réseau, avec un exemple d’appel distant.
- Évolutivité : comparaison verticale et horizontale, avec charge entrante, facteur de capacité et nombre de machines réglables.
- Entraînement maths : douze exercices avec réponse numérique et correction pas à pas, dont l’hypercube à 60 nœuds et la comparaison P2P avec TTL.
- Synthèse du cours : trente thèmes avec recherche, pièges, savoir-faire et références au support ou à l’oral.
- Préparer l’examen : vingt-huit questions à correction masquée, sujet blanc de 90 minutes sur 20, entraînement de 45 minutes et mémo. L’enseignant a annoncé une durée de 90 minutes. Les sujets et barèmes servent à l’entraînement.
- Préparer les TP : simulation de panne avant/après détection, effet de la charge sur le survivant et six étapes avec preuves à produire. La progression est conservée dans le navigateur si son stockage local est disponible ; « Réinitialiser » dans cette rubrique l’efface.

La fiche initiale et le nouveau [guide de révision des cours 1 et 2](guide-revision.pdf) sont accessibles dans l’application. Accès direct aux nouvelles rubriques : `index.html#synthese`, `index.html#examens`, `index.html#tp`.

## Sources et limites

Support d’Olivier Grunder, Cloud et traitements distribués, master DSICS : pages 8 à 9, 15 à 18, 21 et 34 à 35. Livre : Maarten van Steen et Andrew S. Tanenbaum, Distributed Systems, 4e édition, 2023, https://www.distributed-systems.net/index.php/books/ds4/.

Les valeurs sont des exemples calculés, sans mesure d’une infrastructure réelle. La réplication est un scénario simplifié asynchrone avec un nœud d’écriture. La répartition des responsabilités cloud dépend en pratique des services et des contrats.

La comparaison de mise à l’échelle suppose une capacité verticale proportionnelle aux ressources et, en horizontal, des arrivées réparties uniformément dans des files M/M/1 séparées, sans coût de réseau ou de coordination. Elle ne modélise pas une file unique M/M/n. L’évolutivité verticale ne doit pas être confondue avec la distribution verticale des couches décrite page 34 du support.

Les exercices de maths sont proposés pour la révision, pas annoncés comme des questions de l’examen. Leurs références au support et leurs hypothèses sont indiquées dans l’application. L note le nombre moyen de requêtes, appelé N dans le support, pour éviter de le confondre avec le nombre de machines.

La consolidation du 24 octobre 2026 croise le PDF fourni, les notes Word, les exports Plaud du 23 octobre et la fiche initiale. Les apartés privés et les fichiers bruts ne sont pas intégrés au dépôt. L’oral confirme quelques maths appliquées et évoque des VM/load balancing ; dates, pondération et consignes définitives restent à confirmer. Les architectures de la fin du support sont signalées comme suite à préparer, au-delà du contenu de l’enregistrement fourni.

La nouvelle simulation de TP emploie un routage round-robin illustratif et deux files M/M/1 indépendantes. La détection de panne est déclenchée manuellement ; aucun délai réel n’est mesuré. Elle ne décrit pas une politique garantie de Google Cloud et ne crée aucune ressource. Une VM en ligne peut rester saturée ; le répartiteur ne synchronise pas les données.

## Enrichir le cours

Modifier `../Resumes/revisions.json`, puis exécuter `python ../Outils/generer_revisions.py` avec ReportLab installé. Le script régénère le guide PDF et `revision-data.js` depuis la même source. `revision.js` gère l’interface des trois rubriques. Les références détaillées figurent dans la synthèse et à la fin du guide.

## Vérification

Avec Node.js disponible :

```powershell
node --test tests/*.test.cjs
```

Les 16 tests vérifient les modèles de file et de capacité, Chord sur les 288 combinaisons départ/clé, et la coordination par pub/sub, tuples Linda et buffer borné.

La comparaison événements/Linda est un modèle local : pub/sub éphémère sans durabilité ; tous les tuples utilisent le même motif et chaque dépôt crée une occurrence. La simulation reprend les demandes bloquées dans leur ordre d’arrivée pour l’illustration, sans présenter cet ordre comme une garantie de Linda. Le journal des réceptions pub/sub est une trace visuelle, pas une file de rejeu.
