# Cours Cloud

Notes de cours, fiches de notions et exemples à enrichir au fil des séances.

- [Guide pour l’examen de mi-décembre](Atelier/Guide_Cloud_Examen_Mi_Decembre.pdf) · les quatre chapitres expliqués avec un exemple commun et un mini-sujet corrigé.
- [Fiche de formules](Atelier/Fiche_Formules_Maths_Cloud.pdf) · méthodes, unités et calculs des deux supports, avec exemples.

Ces deux PDF sont aussi accessibles dans la rubrique « Préparer l’examen » de l’Atelier. Leurs sources Markdown sont dans `Resumes/`. Pour les actualiser après un nouveau cours, lancer `python Cloud/Cours/Outils/generer_fiches_examen.py` depuis la racine (ReportLab et Arial ou DejaVu Sans).

- [Resumes](Resumes/) : [Fiche 01 illustrée](Resumes/Fiche_01_Cloud_et_systemes_distribues.pdf), [guide consolidé des cours 1 et 2](Resumes/Guide_revision_Cloud_examen_TP.pdf) et données éditables `revisions.json`.
- [Atelier](Atelier/README.md) : douze modules pour comprendre les notions, réviser et préparer les TP ; fonctionnement local, sans build.
- [Schemas](Schemas/) : schéma du middleware en [SVG](Schemas/Schema_middleware.svg) et [PNG](Schemas/Schema_middleware.png).
- [Sources](Sources/README.md) : inventaire des originaux locaux : support du professeur, notes personnelles et exports Plaud.
- [Outils](Outils/) : générateur du guide PDF et des données de l’application.

Les futurs TP officiels sont séparés dans [Cloud/TP](../TP/README.md). La rubrique TP de l’Atelier est un parcours de préparation, pas un TP officiel rendu.

Sous Windows, lancer `Cloud/lancer_atelier_cloud.bat`. Le serveur écoute uniquement sur localhost ; le même BAT avec `-Arreter` permet de l’arrêter.

Les questions, le sujet blanc et le parcours TP sont des entraînements proposés. Seules les indications explicitement entendues sont présentées comme annonces de l’enseignant ; le calendrier, le barème définitif et le matériel autorisé restent à confirmer. Les apartés privés et les sources brutes ne sont pas publiés ici.

Pour enrichir la synthèse, classer le support reçu dans `Sources/Originaux_locaux/`, modifier [revisions.json](Resumes/revisions.json), puis lancer `python Outils/generer_revisions.py` depuis ce dossier (ReportLab et polices Arial sous Windows ou Liberation Sans sous Linux). Le script produit le guide dans `Resumes/` et ses copies/données dans `Atelier/`, sans changer la Fiche 01 initiale. Les PDF embarqués dans l’Atelier sont des copies de diffusion pour permettre le partage autonome de l’application.

Complément du 24 octobre : objets et services (support p. 29), puis Docker et microservices avec sources officielles. Les thèmes 9 et 10 sont disponibles dans le guide et dans la synthèse de l’Atelier. Docker et les microservices ne sont pas présentés comme des sujets d’examen annoncés.

Point noté le 24 octobre : événements, publish/subscribe, couplage temporel/référentiel et espaces de tuples (Linda), support p. 30–31. Le thème 11 est ajouté au guide et à l’Atelier ; le résumé Plaud du matin du 24 octobre est reçu et intégré après comparaison au support.

Linda en clair : page dédiée avec définition, tableau out/rd/in, motif et variables, trace corrigée à deux processus et pièges de blocage. Le même contenu est lisible sous les schémas de l’Atelier.

Architectures des systèmes : trois pages de schémas comparant client-serveur, 3 tiers, services, microservices et P2P sur un même exemple ; même rubrique dans l’Atelier avec parcours pas à pas. Les catégories ne sont pas exclusives et les placements dessinés sont des exemples.

Séance du 24 octobre intégrée : [comparaison et corrections](Resumes/Comparaison_Plaud_2026-10-24.md), ACID/EAI, middleware, Linda/hypercube et calculs économiques de migration. Les exemples numériques sont proposés, les tarifs fictifs, et les informations d’examen issues du seul résumé restent à confirmer.
