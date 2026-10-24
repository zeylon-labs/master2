# Cours Cloud

Notes de cours, fiches de notions et exemples à enrichir au fil des séances.

- [Resumes](Resumes/) : [Fiche 01 illustrée](Resumes/Fiche_01_Cloud_et_systemes_distribues.pdf), [guide consolidé de 13 pages](Resumes/Guide_revision_Cloud_examen_TP.pdf) et données éditables `revisions.json`.
- [Atelier](Atelier/README.md) : dix modules pour comprendre les notions, réviser et préparer les TP ; fonctionnement local, sans build.
- [Schemas](Schemas/) : schéma du middleware en [SVG](Schemas/Schema_middleware.svg) et [PNG](Schemas/Schema_middleware.png).
- [Sources](Sources/README.md) : inventaire des originaux locaux : support du professeur, notes personnelles et exports Plaud.
- [Outils](Outils/) : générateur du guide PDF et des données de l’application.

Les futurs TP officiels sont séparés dans [Cloud/TP](../TP/README.md). La rubrique TP de l’Atelier est un parcours de préparation, pas un TP officiel rendu.

Sous Windows, lancer `Cloud/lancer_atelier_cloud.bat`. Le serveur écoute uniquement sur localhost ; le même BAT avec `-Arreter` permet de l’arrêter.

Les questions, le sujet blanc et le parcours TP sont des entraînements proposés. Seules les indications explicitement entendues sont présentées comme annonces de l’enseignant ; le calendrier, le barème définitif et le matériel autorisé restent à confirmer. Les apartés privés et les sources brutes ne sont pas publiés ici.

Pour enrichir la synthèse, classer le support reçu dans `Sources/Originaux_locaux/`, modifier [revisions.json](Resumes/revisions.json), puis lancer `python Outils/generer_revisions.py` depuis ce dossier (ReportLab et polices Arial Windows). Le script produit le guide dans `Resumes/` et ses copies/données dans `Atelier/`, sans changer la Fiche 01 initiale. Les PDF embarqués dans l’Atelier sont des copies de diffusion pour permettre le partage autonome de l’application.
