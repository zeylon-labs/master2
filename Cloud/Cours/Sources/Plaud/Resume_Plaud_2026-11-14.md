# 11-14 Cours : Systèmes Distribués, Virtualisation et Communication
> Date et heure : 2026-11-14 09:04:11 / 2026-11-14 09:04:11  
> Lieu : [Insérer le lieu]  
> Enseignant : [Insérer le nom de l'enseignant]
## Résumé
La séance traite des principes fondamentaux des systèmes distribués, de la virtualisation, des paradigmes de communication et des modèles architecturaux, tout en intégrant des révisions en vue de l'examen d'une durée de 1h30. 
Après un retour sur les hyperviseurs (Type 1 bare-metal et Type 2 hébergé) et la virtualisation par conteneurs (namespaces, cgroups, PlanetLab/V-servers), le cours aborde la répartition des charges dans les clusters (transfert TCP, DNS, routage sensible au contenu) et les divers modèles de migration de code et de machines virtuelles. 
L'accent est ensuite mis sur les communications distribuées : limites du modèle OSI, rôle central du middleware, comparaison entre communication synchrone/asynchrone et transitoire/persistante, fonctionnement détaillé du RPC (et ses déclinaisons asynchrones), programmation par sockets TCP/IP et utilisation de ZeroMQ. Enfin, la session révise les topologies et styles architecturaux (hypercubes, calcul parallèle/cluster/grille, modèles en couches et REST, Linda et le problème producteur-consommateur), complétée par des échanges sur des retours d'expérience professionnelle et des aspects économiques/logiciels.
---
## Points de connaissance
### 1. Concepts de virtualisation et conteneurs
* **Types de VMM (Virtual Machine Monitor) / Hyperviseurs**
  - **Type 1 (Bare-Metal)** : S’installe directement sur la couche matérielle (*hardware*). Exemples : VMware ESXi, Nutanix, Microsoft Hyper-V. L'installation de Hyper-V requiert Windows Server comme base d'installation, mais modifie l'ordre de démarrage pour exécuter l'hyperviseur au plus près du matériel.
  - **Type 2 (Hébergé)** : S'installe par-dessus un système d'exploitation hôte préexistant depuis un certain temps.
* **Virtualisation par conteneurs**
  - Virtualisation légère au niveau du système d’exploitation, offrant un environnement contrôlé, portable et rapide à démarrer.
  - **Espaces de noms (Namespaces)** : Isolent les ressources (processus/PID, réseau) entre l'hôte et les conteneurs (ex. le PID 1 de l'hôte est distinct du PID 1 du conteneur).
  - **Système de fichiers en couches (Union FS)** : Superposition de couches inférieures en lecture seule (partagées entre conteneurs pour économiser l'espace) et d'une couche supérieure en écriture (*copy-on-write*).
  - **Groupes de contrôle (cgroups)** : Définissent les quotas et priorités d'allocation des ressources matérielles (mémoire, processeur).
* **Architecture PlanetLab et V-servers**
  - Système collaboratif distribué mondialement (fermé en 2020, relayé par des initiatives comme EdgeNet) mutualisant des nœuds de calcul.
  - Utilisation de **V-servers Linux** (précurseurs de Docker) assurant l'étanchéité et l'exécution concurrente sans interférence.
  - Regroupement des serveurs virtuels sous forme de **tranches (*slices*)** pour concevoir des systèmes distribués personnalisés sur réseau étendu (WAN).
### 2. Répartition des requêtes et distribution en cluster
* **Dispatcher et transfert TCP (TCP Handoff)**
  - Le dispatcher peut saturer s'il achemine l'ensemble des flux aller-retour.
  - Avec le transfert TCP, le serveur applicatif reçoit l'adresse du client et lui répond directement sans repasser par le dispatcher, réduisant la bande passante consommée.
* **Routage sensible au contenu**
  - Le répartiteur (ou reverse proxy tel que NGINX) inspecte le contenu/l'URI pour diriger la requête vers le serveur le plus adapté ou le moins chargé.
* **Clusters étendus et résolution DNS**
  - Sur les réseaux étendus (WAN), le DNS oriente le client vers la réplique la plus proche géographiquement afin de minimiser la latence tout en préservant la transparence.
### 3. Migration de code et de machines virtuelles
* **Objectifs de la migration**
  - Équilibrage de la charge entre nœuds d'un centre de données.
  - Réduction des transferts de données en déplaçant le calcul au plus près de la donnée (ex. apprentissage fédéré).
* **Modèles de mobilité de code**
  - **Client-Serveur (Modèle zéro)** : Pas de migration réelle ; le serveur détient et exécute le code sur ses ressources.
  - **Évaluation à distance (*Remote Evaluation*)** : Le client envoie son code au serveur qui l'exécute sur ses ressources (discipline *sender* ; ex. soumission de code Python/C ou programmes d'optimisation).
  - **Code à la demande (*Code on Demand*)** : Le client télécharge le code depuis le serveur et l'exécute localement (ex. JavaScript, applets Java).
  - **Agents mobiles** : Déplacement autonome du code, de l'état d'exécution et des données d'un nœud à un autre (ex. collecte d'informations de proche en proche dans un réseau pair-à-pair).
* **Mobilité faible vs forte et hétérogénéité**
  - *Mobilité faible* : Transfert uniquement du segment de code et des données initiales (redémarrage de zéro).
  - *Mobilité forte* : Déplacement ou clonage du composant avec son état d'exécution complet (threads, contexte).
  - *Gestion de l'hétérogénéité* : Utilisation d'environnements d'exécution abstraits/interprétés (JVM, Python) ou migration d'une machine virtuelle complète.
* **Stratégies de transfert de mémoire pour les VM**
  - **Pré-copie (*Pre-copy*)** : Transfert itératif des pages mémoire pendant que la VM continue de tourner, puis envoi final des pages modifiées (*dirty pages*).
  - **Arrêt et reprise (*Stop-and-Copy*)** : Interruption totale, transfert de l'intégralité de la mémoire, puis redémarrage (génère une indisponibilité notable).
  - **À la demande (*Post-copy / Lazy loading*)** : Redémarrage immédiat sur la cible et rapatriement des pages au fil de leur utilisation par les processus.
### 4. Architectures et paradigmes de communication
* **Limites du modèle OSI et place du Middleware**
  - Le modèle OSI en 7 couches est centré sur le transport de paquets et répond mal au besoin de transparence d'accès.
  - Les systèmes distribués s'appuient sur un modèle à 4 niveaux : Matériel $\rightarrow$ OS $\rightarrow$ Middleware $\rightarrow$ Application.
  - Le middleware gère la sérialisation/désérialisation, le nommage, la sécurité, la tolérance aux pannes et le masquage de l'hétérogénéité.
* **Modes de communication**
  - **Persistante vs Transitoire** : En communication transitoire (ex. RPC, sockets de base), le message disparaît si le récepteur n'est pas actif. En communication persistante (ex. files de messages, e-mail, Linda), le message est conservé par un intermédiaire jusqu'à récupération.
  - **Synchrone vs Asynchrone** : Synchrone impose un blocage de l'émetteur jusqu'à réception/traitement ; Asynchrone libère l'émetteur immédiatement après l'envoi.
* **Appel de procédure à distance (RPC)**
  - Fait abstraction du réseau pour rendre un appel distant semblable à un appel local.
  - Par défaut synchrone et transitoire. Nécessite la sérialisation (gestion de l'endianness, codage des types).
  - *Passage de paramètres* : Passage par valeur obligatoire (ou simulation de référence par copie-restauration).
  - *Variantes asynchrones* : Utilisation d'accusés de réception avec fonction de rappel (*callback*) ou lancement d'appels parallèles non bloquants vers plusieurs répliques.
### 5. Communication orientée messages : Sockets et ZeroMQ
* **Programmation par sockets TCP/IP**
  - Primitives serveur : `socket()`, `bind()` (association IP/port), `listen()` (file d'attente), `accept()` (bloquant), `receive()`, `send()`, `close()`.
  - Primitives client : `socket()`, `connect()`, `send()`, `receive()`, `close()`.
* **ZeroMQ**
  - Abstraction au-dessus des sockets offrant des sémantiques asynchrones avec mise en file d'attente en mémoire vive (la rétention dépend de la vie du processus).
  - **Request/Reply** : Patron client-serveur classique.
  - **Publish/Subscribe** : Diffusion de messages filtrés par mots-clés/motifs aux abonnés.
  - **Pipeline (Push/Pull)** : Répartition unidirectionnelle de tâches depuis des générateurs vers des nœuds travailleurs (*workers*).
  - Autres modèles mentionnés : Routeur/Dealer, Producteur-Consommateur.
### 6. Architectures distribuées, topologies et patrons de synchronisation
* **Catégories de calcul distribué**
  - *Calcul parallèle* : Multiples cœurs/processeurs au sein d'une seule machine physique.
  - *Cluster computing* : Ensemble de serveurs homogènes, colocalisés, reliés par un réseau très rapide et dédié.
  - *Grid computing* : Nœuds hétérogènes, géographiquement distants, sous domaines administratifs multiples.
* **Styles architecturaux et interopérabilité**
  - *Architectures en couches* : Les couches supérieures ($N$) sollicitent les couches inférieures ($N-1$).
  - *Architecture centrée sur les ressources* : Exemple emblématique avec les services REST.
  - *Interopérabilité* : Intégration de composants logiciels non modifiables via des adaptateurs (*adapters*) et des courtiers (*brokers*) pour harmoniser les interfaces.
* **Réseaux superposés (*Overlay Networks*) et décentralisation**
  - Réseaux logiques construits au-dessus de l'infrastructure IP sous-jacente (ex. réseaux P2P, Tor).
  - *Décentralisation* : Indispensable quand la confiance mutuelle fait défaut (blockchain) ou pour des raisons de confidentialité (apprentissage fédéré).
* **Topologie en hypercube**
  - Nombre de sommets égal à $2^d$ ($d$ étant la dimension). Pour héberger 60 serveurs, un hypercube de dimension 6 est requis ($2^6 = 64$ sommets).
  - Gestion des sommets inactifs (4 sommets non attribués) : adaptation de la fonction de hachage pour cibler uniquement les 60 nœuds réels, garantissant la validité du routage bit-à-bit.
* **Modèle Linda et problème Producteur-Consommateur**
  - Espace de tuples partagé avec primitives : `out` (écriture), `in` (lecture destructive), `read` (lecture non destructive).
  - *Limitation de la taille du buffer* : Initialisation de l'espace avec $N$ tuples-jetons représentant les places libres. Le producteur consomme un jeton avec `in` avant d'écrire la donnée ; le consommateur remet un jeton avec `out` après extraction.
### 7. Échanges informels, modèles économiques et vie professionnelle
* **Produits numériques et interface** : Utilisation de tableaux de données dynamiques avec tri côté client sans préchargement intégral pour préserver la mémoire du navigateur.
* **Graphismes et UI** : Développement de shaders avec WebGPU, audit UX/UI, abonnements à des catalogues d'effets visuels (formules mensuelles à ~10€ ou annuelles à ~100€).
* **Parcours et gestion du temps** : Organisation du travail (horaires flexibles, télétravail, amplitudes quotidiennes), transitions professionnelles (prestataire vers interne dans le secteur bancaire au Luxembourg).
---
## Questions
- [Insérer question/confusion]
---
## Tâches et préparation à l'examen
- [ ] 1. **Révisions globales (Épreuve de 1h30)** :
  - Revoir les distinctions fondamentales : Types de VMM (1 vs 2), Calcul parallèle vs Cluster vs Grille, Systèmes décentralisés vs Distribués.
  - Maîtriser l'enchaînement des primitives de sockets TCP/IP (`bind`, `listen`, `accept`, etc.) et les patrons de conception ZeroMQ (Req/Rep, Pub/Sub, Push/Pull).
  - Revoir le protocole DCE RPC, la sérialisation, et les stratégies de synchronisation/persistance.
  - Étudier les architectures logicielles (en couches, REST, adaptateurs/brokers) et les caractéristiques des réseaux superposés.
- [ ] 2. **Exercice Linda** : Analyser et implémenter la limitation de capacité d'un buffer partagé via le mécanisme de jetons d'espaces libres (`in`/`out`).
- [ ] 3. **Exercice de probabilités** : Calculer le nombre maximal de données explorées pour les méthodes de communication présentées (avec une probabilité de découverte de 1 %) et établir le ratio de comparaison.