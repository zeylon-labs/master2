# Cloud et systèmes distribués

> Guide de révision · Master DSICS · Cours 1 et 2 · 14 novembre 2026

L’enseignant annonce un écrit de **1 h 30**, mêlant notions et maths appliquées. Il attend des réponses courtes et accepte un schéma si celui-ci clarifie la réponse. Le périmètre suit la progression d’octobre et du week-end de novembre. La date exacte, le barème, les documents autorisés et les formules à mémoriser restent à confirmer.

Le 14 novembre, la séance s’arrête après ZeroMQ avant les révisions. Priorité à RPC, sockets et ZeroMQ. Les détails de DCE RPC, MPI, messagerie avancée et gossip sont à vérifier pour l’écrit.

## Le fil rouge · Un portail de dépôt de dossiers

Ton navigateur envoie un dossier. Un répartiteur choisit un serveur API. L’API enregistre le dossier, puis publie une tâche qu’un worker peut prendre pour générer un PDF. Plusieurs machines coopèrent derrière une seule interface. Suis quatre questions tout au long du cours.

1. **Où ?** Quel composant fait le travail et où se trouvent les données ?
2. **Quand ?** Qui attend, et la demande peut-elle survivre à une déconnexion ?
3. **Combien ?** À quelle charge la file s’allonge-t-elle, et quel trafic le système génère-t-il ?
4. **Si ça casse ?** Que sait le client et quelles garanties apportent les copies, les confirmations et les reprises ?

## 1 · Comprendre ce qui est distribué

- **Nœuds autonomes.** Chaque machine ou processus exécute sa propre partie. Même avec plusieurs VM, un répartiteur unique peut centraliser le routage. Les pannes peuvent être partielles : l’API répond alors que le worker ou le stockage est inaccessible.
- **Middleware.** Couche logicielle entre l’application et l’OS local. Elle fournit, selon le produit, le nommage, l’encodage des messages, les appels distants ou les files de messages. Au-dessus, le code métier décide quoi faire du dossier.
- **Quatre objectifs.** Partager des ressources, masquer certains détails de distribution, faciliter l’interopérabilité via des interfaces définies, et tenir des changements de taille, de distance ou de domaine administratif.
- **Sept transparences.** Accès (même interface), localisation (même nom), migration (une ressource se déplace), relocalisation (elle se déplace pendant son usage), réplication (les copies sont masquées), concurrence (les usages simultanés sont arbitrés), panne (une reprise est masquée quand c’est possible).
- **Évolutivité.** Augmenter la RAM d’une VM est vertical. Ajouter des VM est horizontal. Un cache rapproche les lectures, le partitionnement répartit des sous-ensembles, la réplication crée des copies. Ces choix peuvent se combiner et créent des besoins distincts de coordination.

> Une file d’attente qui grossit alors que le serveur tourne indique un goulot. Un timeout indique qu’une réponse n’est pas revenue à temps. Si l’API a écrit avant la perte de réponse, une nouvelle tentative peut créer un doublon. Donne à la demande un identifiant stable et explique comment le serveur le déduplique.

Références · C1 p. 10 à 19. Oral du 23/10, 02:37:44 et du 14/11, 02:12:42–02:15:27, 02:41:08–02:41:30. C1 et C2 désignent les pages PDF, couverture comprise. Pour C2, ajouter 34 au numéro PDF à partir de la page 9 pour retrouver le numéro imprimé.

<!-- page -->

# Architectures et coordination

## 2 · Choisir comment les composants collaborent

- **En couches** décrit les responsabilités logicielles. **En trois tiers** décrit ici une architecture séparant présentation, logique métier et données. On peut placer plusieurs instances API dans le même tiers. La distribution verticale sépare des niveaux fonctionnels, tandis que la mise à l’échelle verticale renforce une machine.
- **Services et ressources.** Le service rend un résultat, l’interface précise ce qu’on peut appeler, le protocole fixe les règles d’échange. Un RPC expose par exemple `creerDossier(...)`. Une API REST organise l’échange autour de ressources comme `/dossiers/42`. SOAP est un protocole de messagerie structuré. Les microservices découpent le métier en services déployables, les conteneurs emballent une application et ses dépendances.
- **HTTP.** GET est conçu pour lire et peut laisser des traces techniques. Des PUT identiques sur la même ressource et des DELETE répétés ont le même effet métier visé, même si la deuxième réponse DELETE change. POST peut créer un doublon si l’application ne déduplique pas.
- **Transactions et intégration.** ACID désigne atomicité, cohérence, isolation et durabilité. Un moniteur de transactions coordonne le résultat de sous-transactions compatibles. Pour un effet externe déjà produit, comme un e-mail envoyé, prévoir une autre solution métier lorsque cet effet ne peut être annulé.

## Les deux questions du couplage

| Interaction | Actifs ensemble ? | Destinataire identifié ? |
| --- | --- | --- |
| Appel direct | Oui | Oui |
| Événement éphémère | Oui | Non, on publie sur un sujet |
| Boîte persistante adressée | Non | Oui, via une destination logique |
| Espace de tuples Linda | Non | Non, on sélectionne par motif |

**Linda en trois gestes.** `out` dépose un tuple. `rd` attend un tuple compatible et le lit en le laissant en place. `in` attend puis retire une occurrence compatible. Avec un seul tuple `('ticket', 42)`, deux lecteurs `rd` peuvent le lire. Si un worker réussit `in`, l’autre `in` attend un nouveau tuple qui correspond. Un processus qui retire l’unique ticket avant de tomber en panne peut laisser les autres en attente.

> Cas d’examen. On veut notifier tous les services abonnés à la création d’un dossier. Choisis pub/sub. On veut qu’un worker sélectionne et retire une tâche qui correspond à un motif. Explique le modèle Linda. Pour chacun, dis quand la donnée est disponible et qui la reçoit.

Références · C1 p. 23 et 28 à 34. Plaud 24/10 p. 2 à 5. La persistance d’un pub/sub dépend de son implémentation et de sa configuration.

<!-- page -->

# Charge, Cloud et pair-à-pair

## Voir la saturation avant la panne

Un guichet reçoit 80 dossiers/s et peut en servir 100/s. Il est occupé 80 % du temps. Dans le modèle M/M/1, le traitement prend en moyenne 10 ms mais la réponse prend 50 ms avec l’attente. À 95 dossiers/s, la réponse passe à 200 ms. À 100 dossiers/s, le modèle n’a plus de régime stationnaire. Les formules et les hypothèses sont sur la fiche séparée.

Si deux VM identiques reçoivent 120 dossiers/s au total, chacune reçoit en moyenne 60 dossiers/s sous répartition uniforme. Avec une VM arrêtée et détectée, la survivante reçoit les 120 dossiers/s. L’ajout de deux VM aide la capacité normale, mais ici chacune devrait aussi pouvoir absorber la charge de secours.

## Ce que tu loues et ce que tu conserves

| Offre ou couche | Exemple pour le portail |
| --- | --- |
| Matériel | CPU, stockage physique, réseau et refroidissement. |
| IaaS | Tu loues une VM et gères son OS et l’application. |
| PaaS | Tu déploies ton code sur une plateforme qui gère l’environnement d’exécution. |
| SaaS | Tu utilises un produit web prêt à l’emploi. |

Un **cluster** regroupe des machines coordonnées, souvent dans un environnement homogène. Une **grille** mutualise des ressources à travers des organisations et des environnements différents. **Serverless/FaaS** permet notamment d’exécuter une fonction sur événement avec une gestion de l’infrastructure confiée au fournisseur.

**Décider d’une migration.** Sur le même mois, compare les coûts d’hébergement, de maintenance, de stockage et de flux facturés. Suis séparément local vers cloud et cloud vers local, car tarifs et volumes peuvent différer. Contrôle ensuite les contraintes de délai, de conformité et de continuité métier.

## Trouver une donnée sans serveur central unique

- **DHT/Chord.** On hache la donnée pour obtenir une clé. Sur l’anneau, la clé revient au premier nœud rencontré dans le sens croissant, en revenant au début si nécessaire. Les raccourcis accélèrent la recherche.
- **Hypercube.** L’identifiant est une chaîne de bits. Deux voisins diffèrent d’un bit. De 0000 à 1110, une route minimale est 0000 → 1000 → 1100 → 1110, en trois sauts.
- **P2P non structuré.** L’inondation contacte beaucoup de voisins rapidement et consomme du trafic. Une marche aléatoire explore à peu de frais par étape avec un risque de ne pas trouver avant la limite. Les super-pairs introduisent un niveau d’indexation ou de relais.

Références · C1 p. 16 à 22 et 32 à 39. Plaud 23/10 p. 8 à 10, Plaud 24/10 p. 5 à 6. Le support traite aussi des systèmes omniprésents, notamment des capteurs qui alternent activité et sommeil (C1 p. 24 à 26).

<!-- page -->

# Processus, threads et virtualisation

## 3 · Suivre le travail dans le serveur

Un **processus** offre un espace mémoire et des ressources. Les **threads** d’un processus se partagent notamment le tas, mais chacun possède sa pile et son contexte d’exécution. Ils peuvent se relayer sur un seul cœur (concurrence) et s’exécuter en même temps sur plusieurs cœurs (parallélisme). Deux threads qui écrivent dans une structure partagée ont besoin d’une coordination adaptée.

| Organisation | Le serveur reçoit une demande lente |
| --- | --- |
| Monothread bloquant | Le travail suivant attend que l’appel bloquant rende la main. |
| Dispatcher et workers | Le dispatcher confie les demandes aux workers. Si un worker attend le disque ou le réseau, un autre peut avancer. |
| Boucle d’événements | Les opérations non bloquantes font avancer plusieurs demandes. Une tâche longue qui monopolise la boucle les retarde. |

**Deux niveaux de répartition.** Le load balancer choisit une instance API sur le réseau. Le dispatcher interne choisit un thread ou une tâche dans cette instance. Les threads aident à masquer l’attente d’E/S. Le nombre simultanément actifs se mesure avec le TLP, hors périodes complètement inactives.

## Ce qui est isolé ou déplacé

| Concept | Ce qu’il faut pouvoir expliquer |
| --- | --- |
| VM de processus | Environnement d’exécution pour un programme, par exemple une JVM. |
| Hyperviseur de type 1 | S’exécute directement sur le matériel. Avec Hyper-V, Windows tourne dans la partition racine. |
| Hyperviseur de type 2 | Fonctionne avec un OS hôte et héberge des OS invités. |
| Conteneur | Processus isolés qui partagent le noyau hôte. Les namespaces isolent des vues, les cgroups encadrent l’usage des ressources. |
| Serveur avec état de session | L’instance conserve du contexte entre requêtes. En cas de bascule, le contexte doit être accessible au nouveau serveur pour reprendre. |
| Serveur sans état de session local | Chaque demande contient les informations nécessaires au traitement ou permet de retrouver l’état dans un stockage partagé. |

**Mobilité faible** · Déplacer le code et ses données d’initialisation puis démarrer l’exécution. **Mobilité forte** · Déplacer aussi le contexte pour reprendre en cours d’exécution. Pour une VM, comparer la copie avant bascule (les pages modifiées doivent être recopiées), l’arrêt-copie-redémarrage (coupure pendant la copie) et la copie à la demande après bascule (attentes possibles sur les pages manquantes). Vérifier aussi les liens au stockage et au réseau.

> Pour lire les exemples du PDF. Avec X Window, le serveur X gère écran et entrées près de l’utilisateur. Dans PlanetLab, une tranche regroupe des environnements virtuels sur plusieurs machines. Ces exemples illustrent le rôle des composants et leur placement.

Références · C2 p. 10 à 24 et oral du 14/11, 00:04:25–00:54:55. Un conteneur peut aussi tourner dans une VM.

<!-- page -->

# RPC, messagerie et diffusion

## 4 · Choisir la façon d’échanger

| Besoin | Mécanisme | Point à expliquer |
| --- | --- | --- |
| Obtenir le détail d’un dossier | RPC requête-réponse | Le client attend le résultat de l’appel synchrone. |
| Produire un PDF quand un worker est libre | File persistante | Le broker peut conserver la tâche pendant l’absence du worker, selon la garantie configurée. |
| Prévenir plusieurs abonnés d’un changement | Pub/sub ou multicast | Le groupe de destinataires et la durée de conservation dépendent du système. |
| Rapprocher les versions de données au fil du temps | Gossip | Les répliques échangent périodiquement avec quelques pairs. |

**RPC.** Le stub client encode les arguments, le transport envoie la requête, le stub serveur la décode et appelle la procédure. Le résultat suit le trajet inverse. Une adresse mémoire locale ne désigne pas le même objet sur l’autre machine. Il faut transmettre une valeur, un identifiant ou une référence distante avec un protocole adapté. Un accusé de réception ou d’acceptation est distinct du résultat métier.

**Deux axes.** Jusqu’à quel événement l’appelant attend-il ? Que devient le message si le destinataire est absent ? Ajoute une troisième question pour la durabilité : que se passe-t-il si le processus qui conserve le message s’arrête ?

**TCP et ZeroMQ.** Le serveur TCP prépare `socket → bind → listen → accept`, puis échange sur la socket connectée. ZeroMQ peut mettre les messages en file en mémoire. La file est volatile. Le mode REQ/REP classique alterne envoi et réception, PUB/SUB diffuse aux abonnés, et PUSH/PULL alimente les workers. MPI et les files avancées figurent aussi dans le support.

## Un message pour plusieurs machines

- **Multicast d’application.** Un arbre de diffusion utilise des liens logiques. Plusieurs liens logiques peuvent emprunter le même lien physique. Le stress compte ses traversées. L’élongation compare le délai via l’arbre au plus court chemin physique.
- **Inondation.** Chaque nœud relaie un message nouveau vers ses voisins suivant la règle choisie. Un identifiant aide à éliminer les doublons, et un TTL limite la propagation.
- **Gossip.** En push, un nœud envoie ce qu’il sait. En pull, il demande l’état d’un pair. Push-pull combine les échanges. L’anti-entropie est périodique, tandis qu’une rumeur peut s’arrêter avant d’avoir atteint tout le monde. Une suppression se propage comme une mise à jour spéciale (tombstone) pour éviter la réapparition d’une ancienne valeur.

Références · C2 p. 26 à 41 et oral du 14/11, 01:08:16–01:33:10 et 01:54:34–02:11:33. Multicast et gossip figurent dans le PDF après la partie traitée le 14/11.

<!-- page -->

# Trois exercices du 14 novembre

## Linda · Limiter un buffer à deux places

Écris deux fois `out("libre")` à l’initialisation. Avant chaque `out("buffer", i, valeur)`, le producteur réserve une place avec `in("libre")`. Le consommateur retire le tuple attendu avec `in("buffer", i, ?valeur)`, rend la place avec `out("libre")`, puis affiche la valeur. Après deux dépôts, la troisième production attend. Après un retrait à vide, le consommateur attend la donnée.

## Hypercube · Adresser 60 nœuds et vérifier la route

Pour stocker 50 To à raison de 1 To par nœud, il en faut au moins 50, sans réplication. Sur 60 nœuds, la marge brute vaut 10 To. Comme 2⁵ = 32 et 2⁶ = 64, il faut 6 bits, avec quatre positions vacantes. Si les IDs actifs sont 0 à 59, la route 55 → 63 → 59 échoue sur 63. La route 55 → 51 → 59 reste active et change un bit par saut.

## P2P · Comparer inondation et marche aléatoire

Avec un degré de 10, un TTL de 4 et 1 % de copies, l’inondation idéale explore 10 + 90 + 810 + 7 290 = 8 200 nœuds hors source. La marche effectue au plus quatre contacts. Avec n tests indépendants, la probabilité de succès vaut 1 − 0,99 à la puissance n. Elle est quasi certaine pour l’inondation et vaut 3,94 % pour la marche. La fiche de formules détaille le calcul du ratio P/n.

> À l’écrit, pour la question « extensibilité en taille », explique la scalabilité et ses deux méthodes. Pour illustrer un réseau superposé, montre les liens logiques entre des pairs Chord et le réseau IP qui les transporte.

Références · Oral du 14/11, 02:20:37–02:26:15 et 02:42:30–03:06:16. Anciennes questions, p. 5 à 7. Le guide complet et l’Atelier contiennent le sujet blanc de 90 minutes.

<!-- page -->

# S’entraîner pour l’écrit

Écris les réponses avant de lire le bas de la page. Pour une notion, donne sa définition, un exemple et une limite. Pour un calcul, note tes hypothèses, convertis les unités, écris la relation puis interprète le résultat.

## Mini-sujet · 25 minutes proposées

1. **Timeout.** Après `POST /dossiers`, le réseau coupe avant la réponse. Explique deux états possibles côté serveur et comment éviter de créer le même dossier deux fois.
2. **File M/M/1.** Le serveur reçoit 45 req/s et traite une requête en 20 ms en moyenne. Calcule μ, U, la taille moyenne du système et le temps de réponse. Que change une arrivée à 50 req/s ?
3. **TLP.** Un processus passe 20 % du temps avec 0 thread actif, 50 % avec 1, et 30 % avec 2. Calcule le TLP et interprète-le.
4. **Choix d’architecture.** Pour générer un PDF en arrière-plan et prévenir deux applications quand il est prêt, propose un mécanisme pour chacune des étapes. Que se passe-t-il si le worker chute après avoir publié le fichier mais avant d’acquitter ?
5. **Diffusion.** Sur dix répliques, six ignorent la nouvelle version. Dans le modèle pull du cours, donne la fraction ignorante attendue un tour plus tard. Pourquoi cette valeur peut-elle différer d’un test concret ?

## Corrigé

1. La création peut avoir réussi avant la perte de réponse, ou la demande peut ne pas avoir abouti. Le serveur conserve une clé de déduplication stable, associée au résultat, et traite une répétition de la même demande de façon cohérente.
2. S = 0,020 s, μ = 50 req/s, U = 0,9. En moyenne, 9 requêtes dans le système. R = 1/(50 − 45) = 0,2 s, ou 200 ms. À 50 req/s, U = 1 et les moyennes stationnaires du modèle ne s’appliquent plus.
3. (0,50 + 2 × 0,30)/(1 − 0,20) = 1,375 thread actif en moyenne pendant les périodes actives.
4. Une file persistante alimente le worker. Un événement de disponibilité est publié aux abonnés. Si un acquittement manque, la tâche peut être redélivrée. Un identifiant de dossier stable et une écriture idempotente du résultat limitent les duplications, y compris la répétition éventuelle de l’événement.
5. 0,60² = 0,36, soit 36 % en moyenne sous l’hypothèse d’un tirage uniforme indépendant, avec remise. Un tour réel suit des tirages discrets et dépend du voisinage et de l’implémentation.

## Trois passages avant mi-décembre

- **Compréhension.** Redessine le portail, décris les flèches, puis explique un exemple de panne et un exemple de migration.
- **Calcul.** Reprends M/M/1 et le dimensionnement, puis refais l’hypercube et la comparaison P2P avec un TTL.
- **Simulation d’écrit.** Refais le mini-sujet sur papier, puis le sujet blanc de 90 minutes du guide complet ou de l’Atelier. Reprends les réponses où il manque une hypothèse, une unité ou une justification.

Sources · Supports d’Olivier Grunder `lucc01-cours01-26.pdf` (42 p.) et `lucc01-cours02-26.pdf` (44 p.). Résumés Plaud des 23 et 24 octobre et du 14 novembre. Transcriptions des 23 octobre et 14 novembre.
