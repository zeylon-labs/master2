# Comparaison du résumé Plaud du 24 octobre 2026

Source reçue : résumé du matin, 8 pages. Comparaison avec le support du professeur (42 pages), le guide et la synthèse de l’Atelier. La transcription du 24 octobre n’est pas disponible ici.

| Sujet | Existant | Mise à jour |
|---|---|---|
| Styles et architectures | Couches, services, microservices et cinq schémas | Service/interface/protocole et place du serverless précisés. |
| REST / SOAP | Ressources, méthodes et stateless | Idempotence détaillée : effet attendu, DELETE et réponses, POST avec déduplication. |
| Coordination / Linda | Tableau de couplage et exercice out/rd/in | Tuples ≠ événements persistants ; initialisation des philosophes, compteur et blocages précisés. |
| Middleware / EAI | Communication et adaptateurs évoqués | ACID, TPM, limites du rollback distribué, N(N−1) / 2N et intercepteurs détaillés. |
| P2P | Chord et recherches | Hypercube à 4 bits, route 0→8→12→14, distance de Hamming et comptage de liens ajoutés. |
| Cloud | Couches et responsabilités | Fabrique/matériel, Kubernetes, FaaS/serverless et périmètre des coûts précisés. |
| Rentabilité | Migration brièvement présentée | Méthode forfaitaire, quatre flux après migration et exemple chiffré fictif ajoutés. |

## Corrections importantes

- Un espace de tuples n’est pas simplement un pub/sub persistant : recherche par motif, lecture sans retrait ou retrait d’une occurrence.
- `in` puis `out` assurent une exclusion temporaire sur un tuple unique, mais ne forment pas une instruction atomique globale ; une panne entre les deux peut bloquer les autres processus.
- GET est sûr selon l’effet métier attendu ; une écriture de journal reste possible. POST n’est pas garanti idempotent par sa méthode, mais l’application peut dédupliquer. Une seconde réponse DELETE différente ne suffit pas à invalider l’idempotence.
- Un broker réduit les interfaces, mais peut devenir un goulot ou un point de panne. Les comptages orientés et non orientés doivent être distingués.
- Fabrique/matériel : ressources physiques. Kubernetes gère les charges conteneurisées ; ce n’est ni le matériel ni un PaaS complet universel.
- `S_ij` exige une lecture des unités : si c’est déjà un volume total par période, ne pas le multiplier encore par le nombre de transactions. Les calculs ajoutés définissent explicitement un volume **par transaction**.
- Les bénéfices et coûts doivent utiliser le même horizon ; ne pas soustraire deux fois un coût déjà inclus dans un bénéfice unitaire.

## Informations à confirmer

La mention de schémas avancés de mobilité/capteurs hors examen est rapportée par Plaud p. 2. Elle n’est pas appliquée comme une exclusion certaine du chapitre. La liste « devoirs et plan d’action » reste une proposition tant qu’un énoncé n’est pas fourni. Calendrier et pondération restent à vérifier auprès du professeur.

Les échanges sur les outils personnels, le planning privé et les démarches administratives sont exclus. Le résumé brut est conservé uniquement dans les sources locales ignorées par Git. Les coûts chiffrés sont des exercices, pas des tarifs de fournisseurs.
