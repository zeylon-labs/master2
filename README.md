# Master 2 — Cours et travaux pratiques

Les matières sont séparées à la racine du dépôt.

```text
Secu/
└── TP/
    └── TP_secu_1/       RSA : code, tests, sources, résultats et rapports
Cloud/
├── Cours/
│   ├── Atelier/        Application web et ses PDF embarqués
│   ├── Resumes/        Fiches, guide examen/TP et données de synthèse
│   ├── Schemas/        Schéma du middleware (SVG et PNG)
│   ├── Sources/        Index et originaux disponibles localement
│   └── Outils/         Générateur de la synthèse PDF et des données web
├── TP/                 Emplacement des futurs TP Cloud
└── lancer_atelier_cloud.bat
```

## Cloud

- [Cours et organisation des sources](Cloud/Cours/README.md)
- [Guide de révision, examen et TP](Cloud/Cours/Resumes/Guide_revision_Cloud_examen_TP.pdf)
- [Atelier interactif](Cloud/Cours/Atelier/README.md)
- [Futurs TP Cloud](Cloud/TP/README.md)

Sous Windows, double-cliquer sur [Cloud/lancer_atelier_cloud.bat](Cloud/lancer_atelier_cloud.bat). Le lanceur démarre le serveur en arrière-plan sur **http://127.0.0.1:8765/** et ouvre le navigateur. Un second lancement réutilise le serveur. Python 3.8 ou plus récent suffit, sans bibliothèque à installer. Le runtime Python de Codex est utilisé en secours s’il est présent.

```powershell
.\Cloud\lancer_atelier_cloud.bat
# Arrêter le serveur démarré par le lanceur :
.\Cloud\lancer_atelier_cloud.bat -Arreter
# Si le port est occupé par un autre service :
.\Cloud\lancer_atelier_cloud.bat -Port 8766
```

Sur un autre système, depuis `Cloud/Cours/Atelier`, lancer `python -m http.server 8765 --bind 127.0.0.1`. L’application peut aussi être ouverte directement avec `index.html`.

Les originaux personnels (Word, PDF du professeur et exports Plaud non nettoyés) sont classés dans `Cloud/Cours/Sources/Originaux_locaux/`, exclus de Git. Les synthèses nettoyées et leurs références sont versionnées. Un clone Git ne contient donc pas les originaux privés.

## Sécurité des systèmes d'information

Le dossier [TP_secu_1](Secu/TP/TP_secu_1/) contient le TP RSA : code des parties 1 à 3,
tests, résultats d'exécution et rapport pas à pas en Markdown, Word et PDF.

Les trois fichiers originaux du TP sont rangés dans [sources](Secu/TP/TP_secu_1/sources/).

```powershell
cd Secu/TP/TP_secu_1
python Walter_Arthur_main.py --partie toutes --message "Bonjour Alice"
```

Implémentation pédagogique à petites clés, non destinée à la production.

Pour les démonstrations Windows, lancer `Secu/TP/TP_secu_1/lancer_programmes.bat`. Pour les contrôles, utiliser `Secu/TP/TP_secu_1/lancer_tests_complets.bat`.
