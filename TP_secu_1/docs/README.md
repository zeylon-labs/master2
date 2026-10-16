# Documents du TP RSA

Les deux versions du rapport sont conservées séparément.

| Version | PDF | Word | Source |
| --- | --- | --- | --- |
| Guide détaillé avec explications et prise en main | [Walter_Arthur.pdf](Walter_Arthur.pdf) | [Walter_Arthur.docx](Walter_Arthur.docx) | [Markdown](Walter_Arthur_rapport.md) |
| Compte rendu organisé selon les questions du sujet | [Walter_Arthur_compte_rendu.pdf](Walter_Arthur_compte_rendu.pdf) | [Walter_Arthur_compte_rendu.docx](Walter_Arthur_compte_rendu.docx) | [Markdown](Walter_Arthur_compte_rendu.md) |

Le compte rendu présente les réponses des trois parties, les résultats et les
commentaires. Il conserve seulement les commandes d'exécution et de test,
sans le tutoriel d'installation du guide. Les résultats utilisés sont les mêmes.

Pour régénérer le Word de l'une des versions depuis le dossier TP_secu_1 :

```powershell
python outils/generer_rapport.py --version guide
python outils/generer_rapport.py --version compte-rendu
```

Chaque commande écrit uniquement la version sélectionnée. Exporter ensuite
le Word correspondant en PDF et vérifier la mise en page.

Pour la remise, choisir un seul rapport PDF avec les deux fichiers Python.
Si le compte rendu est choisi, une copie peut être nommée Walter_Arthur.pdf
pour respecter le nom demandé dans l'énoncé. Ne pas joindre les deux rapports
comme s'il s'agissait de deux travaux différents.
