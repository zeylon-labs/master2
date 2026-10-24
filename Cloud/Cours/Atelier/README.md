# Atelier Cloud

Application pédagogique avec dix modules pour comprendre le cours Cloud et traitements distribués, réviser l’examen et préparer les TP.

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
- Middleware : schéma des applications, des instances de middleware, des OS locaux et du réseau, avec un exemple d’appel distant.
- Évolutivité : comparaison verticale et horizontale, avec charge entrante, facteur de capacité et nombre de machines réglables.
- Entraînement maths : huit exercices avec réponse numérique et correction pas à pas sur les files, les probabilités, Little, le dimensionnement, la recherche aléatoire et les capteurs.
- Synthèse du cours : onze thèmes avec recherche, pièges, savoir-faire et références au support ou à l’oral ; aperçu du livre et corrections du résumé automatique.
- Préparer l’examen : douze questions filtrables avec corrections masquées, sujet blanc de 45 minutes sur 20 et mémo des formules. Ce format est proposé pour l’entraînement, pas annoncé par le professeur.
- Préparer les TP : simulation de panne avant/après détection, effet de la charge sur le survivant et six étapes avec preuves à produire. La progression est conservée dans le navigateur si son stockage local est disponible ; « Réinitialiser » dans cette rubrique l’efface.

La fiche initiale et le nouveau [guide de révision et TP de 15 pages](guide-revision.pdf) sont accessibles dans l’application. Accès direct aux nouvelles rubriques : `index.html#synthese`, `index.html#examens`, `index.html#tp`.

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
node --test tests/model.test.cjs
```

Les tests vérifient le modèle de file, le parcours Chord du support, le bouclage de l’anneau et les 288 combinaisons départ/clé.
