# Atelier Cloud

Petite application pédagogique associée à la fiche 01, pour manipuler quatre notions du cours Cloud et traitements distribués.

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

Chaque module propose une question avec correction. La fiche PDF est accessible dans l’application.

## Sources et limites

Support d’Olivier Grunder, Cloud et traitements distribués, master DSICS : pages 8 à 9, 15 à 18, 21 et 34 à 35. Livre : Maarten van Steen et Andrew S. Tanenbaum, Distributed Systems, 4e édition, 2023, https://www.distributed-systems.net/index.php/books/ds4/.

Les valeurs sont des exemples calculés, sans mesure d’une infrastructure réelle. La réplication est un scénario simplifié asynchrone avec un nœud d’écriture. La répartition des responsabilités cloud dépend en pratique des services et des contrats.

## Vérification

Avec Node.js disponible :

```powershell
node --test tests/model.test.cjs
```

Les tests vérifient le modèle de file, le parcours Chord du support, le bouclage de l’anneau et les 288 combinaisons départ/clé.
