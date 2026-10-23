# Atelier Cloud

Petite application pédagogique associée à la fiche 01, avec sept modules pour explorer le cours Cloud et traitements distribués et s’entraîner aux calculs.

## Utilisation

Ouvrir `index.html` dans un navigateur. Les interactions et les calculs fonctionnent localement, sans installation. La police distante est facultative : une police système est utilisée hors ligne.

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

Les modules de notions proposent une question avec correction. La fiche PDF est accessible dans l’application.

## Sources et limites

Support d’Olivier Grunder, Cloud et traitements distribués, master DSICS : pages 8 à 9, 15 à 18, 21 et 34 à 35. Livre : Maarten van Steen et Andrew S. Tanenbaum, Distributed Systems, 4e édition, 2023, https://www.distributed-systems.net/index.php/books/ds4/.

Les valeurs sont des exemples calculés, sans mesure d’une infrastructure réelle. La réplication est un scénario simplifié asynchrone avec un nœud d’écriture. La répartition des responsabilités cloud dépend en pratique des services et des contrats.

La comparaison de mise à l’échelle suppose une capacité verticale proportionnelle aux ressources et, en horizontal, des arrivées réparties uniformément dans des files M/M/1 séparées, sans coût de réseau ou de coordination. Elle ne modélise pas une file unique M/M/n. L’évolutivité verticale ne doit pas être confondue avec la distribution verticale des couches décrite page 34 du support.

Les exercices de maths sont proposés pour la révision, pas annoncés comme des questions de l’examen. Leurs références au support et leurs hypothèses sont indiquées dans l’application. L note le nombre moyen de requêtes, appelé N dans le support, pour éviter de le confondre avec le nombre de machines.

## Vérification

Avec Node.js disponible :

```powershell
node --test tests/model.test.cjs
```

Les tests vérifient le modèle de file, le parcours Chord du support, le bouclage de l’anneau et les 288 combinaisons départ/clé.
