# Master 2 Travaux pratiques

## Sécurité des systèmes d'information

Le dossier [TP_secu_1](TP_secu_1/) contient le TP RSA : code des parties 1 à 3,
tests, résultats d'exécution et rapport pas à pas en Markdown, Word et PDF.

Les trois fichiers originaux du professeur sont rangés dans [TP_secu_1/sources](TP_secu_1/sources/).

```powershell
cd TP_secu_1
python Walter_Arthur_main.py --test
python Walter_Arthur_main.py --partie toutes --message "Bonjour Alice"
```

Implémentation pédagogique à petites clés, non destinée à la production.

Pour voir les démonstrations dans la console sous Windows, lancer `TP_secu_1/lancer_programmes.bat`. Pour les contrôles automatiques, utiliser `TP_secu_1/lancer_tests_complets.bat`.
