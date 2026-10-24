window.CloudStudy = {
  "date": "24 octobre 2026",
  "scope": "Synthèse du support fourni (42 pages), des notes Word, de la transcription et du résumé Plaud du 23 octobre, complétée par les fiches et simulations existantes. L’enregistrement s’arrête pendant l’introduction aux systèmes HPC ; les architectures de la suite du PDF sont aussi à travailler, sans les présenter comme déjà traitées oralement.",
  "evidence": [
    {
      "label": "Annoncé oralement",
      "text": "L’examen comporte quelques questions de mathématiques appliquées aux systèmes distribués, et aussi des questions non mathématiques. Transcription du 23/10, 02:37:44 (p. 63)."
    },
    {
      "label": "Pratique évoquée",
      "text": "Machines virtuelles et équilibrage de charge sur Google Cloud. Transcription, 00:03:28–00:04:09 (p. 2). Le parcours TP ci-dessous est un entraînement proposé, pas le sujet officiel."
    },
    {
      "label": "À confirmer",
      "text": "Les dates exactes, la durée définitive, les documents autorisés et le barème des évaluations. Le Word et l’oral évoquent un écrit en décembre et un final ; la pondération 50/25/25 évoquée à 00:07:35 ne constitue pas une consigne officielle stabilisée ici."
    },
    {
      "label": "Priorités proposées",
      "text": "Les priorités ci-dessous reposent sur le support et l’insistance de l’oral. Elles ne prédisent ni le sujet ni la probabilité d’une question. Les suggestions de Plaud ne sont pas reprises comme devoirs donnés par le professeur."
    }
  ],
  "topics": [
    {
      "id": "fondements",
      "title": "1 · Nœuds autonomes, pannes partielles et middleware",
      "priority": "Socle",
      "source": "Support p. 11–15 et 19 ; oral 01:17:44–01:22:14 et 01:32:58–01:34:42",
      "route": "middleware",
      "points": [
        "Un système distribué fait coopérer des nœuds autonomes pour fournir un service cohérent. Un nœud peut être une machine ou un processus. Les machines conservent leurs OS locaux et leurs horloges.",
        "Un système physiquement distribué peut garder un contrôle central. La décentralisation concerne aussi l’organisation du contrôle ; multiplier les machines ne suffit pas à la démontrer.",
        "Le middleware se place entre les applications et les OS locaux : RPC, messagerie, nommage ou sécurité selon le produit. Ses instances coopèrent à travers le réseau. L’expression « OS des systèmes distribués » est une analogie.",
        "Une panne peut ne toucher qu’un composant. Un timeout indique l’absence de réponse à temps, sans prouver que l’opération n’a pas été exécutée. Réessayer une écriture peut donc la dupliquer."
      ],
      "trap": "Ne pas supposer un réseau fiable, sûr, homogène ou statique ; ni une latence nulle, une bande passante infinie, des transferts gratuits ou une administration unique.",
      "task": "Dessine deux machines avec application → middleware → OS → matériel, puis montre le trajet d’un appel distant."
    },
    {
      "id": "objectifs",
      "title": "2 · Objectifs, transparence et ouverture",
      "priority": "Socle",
      "source": "Support p. 13–15 ; oral : objectifs et formes de transparence",
      "route": "donnees",
      "points": [
        "Quatre objectifs : partager les ressources, masquer les détails utiles à masquer, permettre l’interopérabilité et passer à l’échelle.",
        "Sept transparences : accès (formats/méthodes), localisation (où), migration (déplacement), relocalisation (déplacement pendant l’usage), réplication (copies), concurrence (accès simultanés), panne (défaillance/reprise).",
        "Masquer l’existence de copies ne garantit pas leur cohérence immédiate. Les garanties de cohérence dépendent du protocole choisi et du coût de coordination accepté.",
        "Ouverture : interfaces publiées et compatibles, portabilité et remplacement de composants. Séparer politique (objectif/règle, par exemple durée de validité du cache) et mécanisme (moyen, par exemple horodatage et invalidation). Ouvert ne veut pas dire sans authentification."
      ],
      "trap": "La transparence a un coût et des limites : une application peut avoir besoin d’exposer l’emplacement, la latence ou un échec.",
      "task": "Pour chaque forme de transparence, donne un exemple concret et une limite."
    },
    {
      "id": "echelle",
      "title": "3 · Évolutivité et gestion des copies",
      "priority": "Socle",
      "source": "Support p. 15–18 ; oral 02:34:34–02:36:26",
      "route": "evolutivite",
      "points": [
        "Trois dimensions : taille (utilisateurs/nœuds), géographie (distance/latence) et administration (organisations/règles). L’extensibilité ajoute des fonctions ; elle ne se confond pas avec la tenue en charge.",
        "Verticale : augmenter CPU/RAM/stockage d’une machine. Horizontale : ajouter des machines et répartir le travail. Ni l’une ni l’autre ne supprime automatiquement le goulot de la base ou du réseau.",
        "Partitionner répartit des données différentes ; répliquer crée plusieurs copies ; un cache conserve une copie pour accélérer les accès. Le partitionnement seul n’ajoute pas de redondance.",
        "L’asynchronisme masque une attente et libère des ressources ; il ne rend pas le réseau instantané. Déporter du calcul côté client peut réduire la charge, mais les contrôles de sécurité restent nécessaires côté serveur."
      ],
      "trap": "Distribution verticale des couches (support p. 34) et mise à l’échelle verticale d’une machine sont deux notions différentes. Un répartiteur ne synchronise pas les données.",
      "task": "Diagnostique d’abord CPU, stockage ou réseau ; propose ensuite une solution et explique ce qu’elle coûte."
    },
    {
      "id": "files",
      "title": "4 · File M/M/1 : comprendre avant de calculer",
      "priority": "Maths annoncées ; modèle central du support",
      "source": "Support p. 16–17 ; oral 02:06:28–02:23 environ",
      "route": "maths",
      "points": [
        "Hypothèses : arrivées Poisson de taux λ, services exponentiels indépendants de taux μ, un serveur, file de capacité illimitée. Régime stationnaire stable : λ < μ. S = 1/μ est le traitement moyen, R inclut l’attente.",
        "U = λ/μ ; pₖ = (1 − U)Uᵏ pour k ≥ 0 ; p₀ = 1 − U ; L = U/(1 − U). L est le nombre moyen dans le système, attente ET service, noté N dans le cours.",
        "R = 1/(μ − λ) = S/(1 − U). Attente W = R − S. Loi de Little : L = λR avec des moyennes stables et le même périmètre ; cette loi n’exige pas, à elle seule, un modèle M/M/1.",
        "Exemple : λ = 80 req/s, S = 10 ms = 0,010 s, μ = 100 req/s. U = 0,8 ; R = 50 ms ; W = 40 ms ; L = 4 ; p₀ = 20 % ; p₂ = 0,2 × 0,8² = 12,8 %."
      ],
      "trap": "À λ ≥ μ, ne pas appliquer les formules stationnaires. Le serveur ne s’arrête pas instantanément : la file n’a plus de régime stationnaire stable dans ce modèle.",
      "task": "Refais la dérivation : λpₖ = μpₖ₊₁, puis somme géométrique Σpₖ = 1, puis Little."
    },
    {
      "id": "cloud",
      "title": "5 · ASP, cloud, cluster et grid",
      "priority": "Socle",
      "source": "Support p. 8–10 et 19–22",
      "route": "cloud",
      "points": [
        "ASP = Application Service Provider : prestataire qui héberge une application et en loue l’usage. Les ASP historiques précèdent les offres SaaS modernes ; un accès navigateur n’est pas la seule forme possible.",
        "IaaS : ressources d’infrastructure, avec OS et application à exploiter côté client. PaaS : plateforme gérée pour déployer du code. SaaS : application prête à utiliser. La répartition précise dépend du service/contrat ; accès et données demandent toujours une gestion côté client.",
        "Cluster : ensemble de machines souvent homogènes sous une administration commune, réseau local rapide. Grid : ressources plus hétérogènes, souvent réparties entre organisations. Cloud : ressources accessibles comme services ; ce terme ne signifie pas simplement beaucoup de serveurs.",
        "Une migration doit considérer le coût du calcul ET des transferts, la latence, les données, les contraintes et la disponibilité. Une solution moins chère par requête peut coûter davantage à cause des échanges."
      ],
      "trap": "Ne pas traiter les chiffres matériels donnés comme exemples comme des définitions universelles des clusters.",
      "task": "Pour une VM, un environnement de déploiement géré et une messagerie prête à utiliser, identifie l’offre et ce que le client administre."
    },
    {
      "id": "architectures",
      "title": "6 · Couches, services et messages",
      "priority": "Suite du PDF à préparer",
      "source": "Support p. 23–24 et 28–33 ; complément HTTP RFC 9110",
      "route": "middleware",
      "points": [
        "Couche = séparation logique des responsabilités ; tiers = déploiement sur une machine/processus distinct. Présentation, logique métier et données peuvent être trois couches sur une machine ou réparties sur plusieurs tiers.",
        "RPC : appeler une opération distante avec une abstraction d’appel. Il reste des latences, des échecs et des résultats incertains. MOM : échanges via une infrastructure de messages ; persistance et livraison dépendent du produit et de sa configuration.",
        "REST organise l’accès à des ressources par des représentations et une interface uniforme. Stateless signifie que le serveur ne dépend pas d’un contexte de session client conservé entre requêtes ; il peut conserver les données métier.",
        "GET lit ; PUT crée ou remplace l’état de la ressource cible ; POST demande un traitement selon la ressource cible. Ne pas mémoriser la simplification « PUT = créer, POST = modifier ».",
        "Publication/abonnement : producteurs et consommateurs passent par des sujets/événements. Le découplage dans l’espace et dans le temps dépend du système ; une livraison durable exige des mécanismes adaptés. Linda : out écrit un tuple, in retire un tuple correspondant, rd le lit sans le retirer."
      ],
      "trap": "Dans le modèle du support : N(N − 1) adaptateurs orientés entre N applications, contre 2N via un intermédiaire. Ce n’est pas un comptage de câbles physiques.",
      "task": "Compare un appel RPC bloquant et un message asynchrone pour traiter une commande."
    },
    {
      "id": "p2p",
      "title": "7 · P2P, Chord et recherches",
      "priority": "Suite du PDF à préparer",
      "source": "Support p. 34–39",
      "route": "chord",
      "points": [
        "P2P structuré : règles de placement et de routage (DHT). Dans Chord, une clé est portée par son successeur : premier nœud actif dans le sens horaire atteignant ou dépassant la clé, avec retour à zéro.",
        "Exemple du support : identifiants sur 5 bits, donc 32 positions possibles, mais 9 nœuds actifs. Clé 3 depuis 9 : 9 → 28 → 1 → 4. Le nœud 4 porte la clé. Clé 30 : responsable 1 après bouclage.",
        "Les fingers utilisent des départs n + 2ⁱ modulo 2ᵐ puis leurs successeurs. On choisit un raccourci précédant la cible ; un saut final rejoint son responsable.",
        "Non structuré : inondation ou marche aléatoire. Avec sondages uniformes indépendants et r copies sur N nœuds, E[K] ≈ N/r. Ce nombre est une moyenne, pas une garantie ni nécessairement une mesure de réseau réel.",
        "Superpairs, edge et distribution de fragments sont d’autres organisations. Les exemples historiques du support illustrent des principes, pas nécessairement le fonctionnement actuel des produits cités."
      ],
      "trap": "Une couche overlay est un graphe logique. La formule d(d − 1)^(k − 1) décrit une frontière idéale d’inondation, pas un total cumulé ni un réseau réel avec boucles.",
      "task": "Explique le responsable d’une clé, puis justifie chaque saut sans confondre identifiant possible et nœud actif."
    },
    {
      "id": "autres",
      "title": "8 · Transactions, mobilité et énergie",
      "priority": "Suite du PDF à préparer",
      "source": "Support p. 23–26",
      "route": "maths",
      "points": [
        "Une transaction regroupe des opérations avec une décision de validation ou d’abandon. L’atomicité impose tout ou rien ; envoyer plusieurs appels réseau ne suffit pas à fournir cette propriété.",
        "Les systèmes mobiles et capteurs doivent gérer déconnexions, ressources limitées et consommation. Pour un capteur : τ = T_actif/(T_actif + T_sommeil). Avec 2 s actives et 8 s de sommeil, τ = 20 %.",
        "Le mode hors ligne d’une PWA nécessite une stratégie de cache et de synchronisation. Un service worker ne résout pas automatiquement les conflits lors de la reconnexion."
      ],
      "trap": "Un pourcentage de temps actif n’est pas directement un pourcentage d’énergie économisée : il faut aussi connaître les puissances et coûts de transition.",
      "task": "Décris ce qui arrive à une écriture faite hors ligne si la même donnée a été modifiée ailleurs."
    },
    {
      "id": "objets-services",
      "title": "9 · Architectures orientées objet et services",
      "priority": "Support p. 29 ; comparaison SOA : complément pédagogique",
      "source": "Support p. 29, section 2.1.2 ; synthèse et exemple proposés",
      "route": "middleware",
      "points": [
        "Orientée objet : les composants encapsulent un état et exposent des méthodes. Exemple : un objet Panier contient des lignes et propose ajouterProduit(). Son implémentation reste cachée. Il peut être local ; s’il est distant, un proxy et un middleware peuvent transporter l’appel sur le réseau.",
        "Un appel de méthode distant ressemble à un appel local dans le code, mais ajoute sérialisation, latence et pannes partielles. Un timeout ne prouve pas que la méthode n’a pas modifié l’objet. Ni les classes ni l’encapsulation ne suppriment les contraintes du distribué.",
        "Orientée services (SOA) : organiser des capacités métier derrière des contrats explicites. Exemple : un service Paiement propose une opération autoriserPaiement(), utilisée par plusieurs applications sans exposer son code interne. HTTP/REST, RPC ou des messages sont des moyens de communication possibles.",
        "Les deux approches sont compatibles : un service peut être développé avec des objets. Objet décrit surtout la structure du composant et son interface ; service décrit une capacité accessible par contrat. Une architecture SOA n’impose ni un protocole unique ni un bus central obligatoire."
      ],
      "trap": "Un objet distant n’est pas automatiquement un microservice : il faut aussi considérer le découpage métier et l’autonomie de déploiement.",
      "task": "Compare Panier.ajouterProduit() et le contrat d’un service Commandes ; explique ce qui change si l’appel traverse le réseau."
    },
    {
      "id": "docker-microservices",
      "title": "10 · Microservices et Docker : deux rôles différents",
      "priority": "Complément pédagogique ; pas un sujet d’examen confirmé",
      "source": "Documentation officielle Docker et Microsoft Azure Architecture Center ; sources en fin de guide",
      "route": "cloud",
      "points": [
        "Microservices : découper une application par capacités métier autonomes, déployables indépendamment. Dans une boutique : Catalogue, Commandes, Paiement. On peut multiplier les instances du seul Catalogue. Chaque service maîtrise ses données et ses contrats ; une base physique distincte par service n’est pas une obligation universelle.",
        "Le gain d’autonomie demande de gérer réseau, timeouts, sécurité et diagnostic entre services. Si le paiement échoue après la création d’une commande, l’ensemble n’est pas automatiquement annulé : il faut prévoir états, reprise ou compensation. Un monolithe modulaire peut rester un meilleur choix pour une petite application.",
        "Docker sert à construire et exécuter des conteneurs. Image : modèle de fichiers et configuration ; conteneur : processus isolé créé depuis une image. Dockerfile : recette de construction ; registre : stockage des images ; volume : données conservées indépendamment du conteneur. Compose décrit et lance plusieurs services conteneurisés.",
        "Une VM possède son noyau invité ; les conteneurs Linux partagent le noyau de l’hôte Linux. Sur Windows, Docker Desktop peut fournir cet hôte via une VM ou WSL 2. Plusieurs conteneurs sur un même hôte ne protègent pas d’une panne de cet hôte."
      ],
      "trap": "Docker n’est pas une architecture microservices : on peut conteneuriser un monolithe et exécuter des microservices sans Docker. Compose ne transforme pas un projet en cluster tolérant aux pannes.",
      "task": "Dessine Client → Catalogue / Commandes → Paiement ; place un conteneur par service, puis montre ce qui reste partagé sur l’hôte."
    },
    {
      "id": "evenements-espaces",
      "title": "11 · Événements, publish/subscribe et espaces partagés",
      "priority": "Support p. 30–31 ; point signalé pendant la séance du 24 octobre",
      "source": "Support p. 30–31, sections 2.1.4.1 à 2.1.4.3 ; récap Plaud de la séance à intégrer dès réception",
      "route": "evenements",
      "points": [
        "Un événement décrit un fait survenu, par exemple CommandeCréée. Dans publish/subscribe, un producteur publie sur un sujet (topic) ou un bus ; les abonnés intéressés reçoivent une notification. Exemple : Email et Stock réagissent à la même commande sans que le service Commandes connaisse chacun de leurs destinataires.",
        "Couplage référentiel : faut-il désigner le destinataire pour communiquer ? Le découplage référentiel permet de passer par un sujet ou de chercher une donnée par son contenu. Couplage temporel : les participants doivent-ils être disponibles en même temps ? Le découplage temporel demande qu’un intermédiaire conserve ce qui doit être récupéré plus tard.",
        "La grille du cours compare quatre modèles : échange direct = couplage temporel et référentiel ; événement éphémère = couplage temporel, découplage référentiel ; boîte aux lettres persistante adressée = découplage temporel, couplage référentiel ; espace de données partagé avec conservation des tuples = découplage temporel et référentiel.",
        "Nuance : publish/subscribe n’implique pas automatiquement de perdre les événements hors ligne, ni de pouvoir les rejouer. Cela dépend de la conservation, des abonnements et des garanties du système. Redis Pub/Sub classique, par exemple, ne rejoue pas les messages manqués après une déconnexion. Un mécanisme durable configuré pour conserver les messages peut fournir un découplage temporel.",
        "Dans un espace de données partagé de type Linda, un producteur dépose un tuple, par exemple (commande, 42, prête). Le consommateur cherche un tuple correspondant à un motif, sans identifier son producteur. Le support précise : out(t) ajoute un tuple ; rd(motif) lit une copie sans retirer le tuple ; in(motif) récupère et retire un tuple correspondant. in et rd attendent si aucun tuple ne correspond ; deux out identiques créent deux occurrences.",
        "Lien avec les microservices : un service Commandes peut publier CommandeCréée ; Stock et Email réagissent indépendamment. Publication ne signifie pas que tous ont déjà traité l’événement. Réessais, doublons et ordre dépendent des garanties ; identifier les événements et rendre certains traitements idempotents aide à éviter de répéter un effet."
      ],
      "trap": "Asynchrone ne signifie pas durable. Un espace de tuples n’est ni une mémoire RAM commune à tous les OS ni une diffusion automatique vers tous les abonnés : in et rd sélectionnent des tuples par motif.",
      "task": "Classe un appel direct, un topic éphémère, une boîte aux lettres persistante et Linda selon les deux couplages. Puis explique ce qui arrive si le consommateur est absent lors de la publication."
    }
  ],
  "formulas": [
    [
      "Capacité et utilisation",
      "μ = 1/S ; U = λ/μ",
      "S en secondes si μ est en req/s."
    ],
    [
      "Probabilités M/M/1",
      "pₖ = (1 − U)Uᵏ ; p₀ = 1 − U",
      "k entier ≥ 0 ; régime stable."
    ],
    [
      "Nombre et réponse",
      "L = U/(1 − U) ; R = 1/(μ − λ) ; W = R − S",
      "L compte attente et service ; R, W, S en secondes."
    ],
    [
      "Little",
      "L = λR",
      "Moyennes stables, même système et mêmes unités."
    ],
    [
      "Machines idéales",
      "n_min = plafond[λ/(U_max μ)]",
      "n ≥ 1 ; 0 < U_max < 1 ; charge uniforme, serveurs identiques."
    ],
    [
      "Après une panne",
      "U = λ/((n − 1)μ)",
      "n > 1 ; même demande répartie sur les survivants ; vérifier U < 1."
    ],
    [
      "Copies / capteur",
      "E[K] ≈ N/r ; τ = T_actif/(T_actif + T_sommeil)",
      "Recherche indépendante uniforme ; cycle de service ≠ énergie exacte."
    ]
  ],
  "questions": [
    {
      "category": "Concepts",
      "q": "Pourquoi un timeout ne prouve-t-il pas l’échec d’une écriture ?",
      "a": "La demande peut avoir été traitée puis la réponse perdue ou retardée. Avant de réessayer, utiliser selon le besoin un identifiant de requête, une opération idempotente ou un mécanisme de déduplication. Un timeout seul ne distingue pas lenteur, coupure et panne.",
      "source": "Support p. 14 et 19 ; oral 01:32:58–01:34:42"
    },
    {
      "category": "Concepts",
      "q": "Le middleware remplace-t-il les OS ? Dessine ses couches.",
      "a": "Non. Sur chaque machine : application → middleware → OS local → matériel. Les instances coopèrent à travers les OS et le réseau. Elles fournissent par exemple RPC ou messagerie.",
      "source": "Support p. 13"
    },
    {
      "category": "Concepts",
      "q": "Deux bases contiennent des données différentes. Est-ce une réplication ?",
      "a": "Si elles se partagent des sous-ensembles distincts, c’est un partitionnement. Si chacune contient une copie d’une même donnée, c’est de la réplication. On peut combiner les deux en répliquant chaque partition.",
      "source": "Support p. 18"
    },
    {
      "category": "Maths",
      "q": "λ = 80 req/s, S = 10 ms : calculer μ, U, R, W, L et p₂.",
      "a": "S = 0,010 s ; μ = 100 req/s ; 80 < 100 donc stable. U = 0,8 ; R = 1/20 s = 50 ms ; W = 50 − 10 = 40 ms ; L = 80 × 0,05 = 4 ; p₂ = 0,2 × 0,8² = 0,128 = 12,8 %. L inclut le service.",
      "source": "Support p. 16–17"
    },
    {
      "category": "Maths",
      "q": "Comment retrouver pₖ sans apprendre sa formule seule ?",
      "a": "L’équilibre local donne λpₖ = μpₖ₊₁, donc pₖ = Uᵏp₀. Pour U < 1, ΣUᵏ = 1/(1 − U). La normalisation Σpₖ = 1 impose p₀ = 1 − U. Ainsi pₖ = (1 − U)Uᵏ.",
      "source": "Support p. 16 ; démonstration orale"
    },
    {
      "category": "Maths",
      "q": "λ = 500 req/s, μ = 100 req/s par machine, U ≤ 80 % : combien de machines ? Et pour tenir le même objectif après une panne ?",
      "a": "Charge uniforme : n ≥ 500/(0,8 × 100) = 6,25, donc 7 machines. Pour garder cet objectif après la perte d’une machine, il faut n − 1 ≥ 6,25, donc 8 au départ. Cette marge est un exercice proposé, sous ces seules hypothèses.",
      "source": "Application proposée des p. 15–18"
    },
    {
      "category": "Maths",
      "q": "À μ = 100 req/s, passer de λ = 80 à 95 req/s multiplie R par combien ?",
      "a": "R₁ = 1/(100 − 80) = 0,05 s. R₂ = 1/(100 − 95) = 0,20 s. Le temps de réponse est multiplié par 4, alors que les arrivées n’augmentent que de 18,75 %. La proximité de saturation explique cet effet non linéaire.",
      "source": "Support p. 16–17"
    },
    {
      "category": "Architectures",
      "q": "Trois couches imposent-elles trois machines ? Que signifie stateless ?",
      "a": "Non : les couches sont logiques et les tiers décrivent le déploiement. Stateless signifie que chaque requête apporte le contexte nécessaire au traitement sans dépendre d’une session client stockée entre requêtes ; cela n’interdit pas une base de données métier.",
      "source": "Support p. 28–31"
    },
    {
      "category": "Architectures",
      "q": "Dans l’anneau du cours, qui porte les clés 3, 12 et 30 ?",
      "a": "Nœuds actifs : 1, 4, 9, 11, 14, 18, 20, 21, 28. Les responsables sont 4, 14 et 1. Pour 30, on dépasse le dernier nœud puis on revient au premier. Il n’y a pas un serveur pour chaque identifiant.",
      "source": "Support p. 34–35"
    },
    {
      "category": "Maths",
      "q": "10 000 nœuds, 10 copies : combien de sondages en moyenne ? Capteur actif 2 s puis endormi 8 s : quel cycle ?",
      "a": "Sondages indépendants uniformes : E[K] ≈ 10 000/10 = 1 000, sans garantie de maximum. Cycle actif : τ = 2/(2 + 8) = 0,2 = 20 %. Ne pas diviser uniquement par le temps de sommeil.",
      "source": "Support p. 26 et 36"
    },
    {
      "category": "TP",
      "q": "Ajouter un load balancer double-t-il la capacité et synchronise-t-il les données ?",
      "a": "Non. Il distribue les requêtes vers des backends. Le gain dépend de leur capacité, de la répartition et des goulots partagés. Les données, sessions et écritures ont besoin de mécanismes spécifiques ; les health checks détectent une indisponibilité avec un délai.",
      "source": "Entraînement lié au TP évoqué ; support p. 18"
    },
    {
      "category": "TP",
      "q": "Deux VM servent des pages différentes après équilibrage. Comment diagnostiquer ?",
      "a": "Afficher l’identité/version de chaque backend, vérifier le déploiement et la configuration, examiner les logs et le cache. Répéter des requêtes n’impose pas une alternance stricte ; l’affinité et la politique du répartiteur peuvent maintenir un même backend.",
      "source": "Entraînement proposé VM et load balancing"
    }
  ],
  "mock": [
    {
      "title": "A · Expliquer — 5 points",
      "prompt": "Dessiner les couches de deux nœuds, situer le middleware, expliquer une panne partielle et deux transparences avec leurs limites.",
      "rubric": "Schéma correct 2 pts ; panne et incertitude 1 pt ; transparences et limites 2 pts."
    },
    {
      "title": "B · Calculer — 7 points",
      "prompt": "Pour λ = 80 req/s et S = 10 ms, établir la stabilité, calculer U, R, W, L, p₂. Puis calculer R pour λ = 95 req/s et interpréter.",
      "rubric": "Unités et stabilité 1 pt ; U/R/W 2 pts ; L/p₂ 2 pts ; comparaison et interprétation 2 pts. Correction : 80 %, 50 ms, 40 ms, 4, 12,8 %, puis 200 ms (×4)."
    },
    {
      "title": "C · Dimensionner — 4 points",
      "prompt": "À λ = 500 req/s et μ = 100 req/s par VM, viser U ≤ 80 %. Dimensionner avec puis sans la perte d’une VM. Donner deux limites du modèle.",
      "rubric": "7 VM sans panne 1 pt ; 8 VM pour tenir l’objectif après une panne 1 pt ; deux limites argumentées 2 pts : déséquilibre, coûts réseau, base commune, détection de panne…"
    },
    {
      "title": "D · Architecturer et diagnostiquer — 4 points",
      "prompt": "Proposer un client → répartiteur → deux VM → stockage partagé. Distinguer répartition et réplication. Expliquer quoi mesurer lors d’une panne et retrouver le responsable de la clé 30 dans Chord.",
      "rubric": "Architecture et données 1 pt ; mesures/health checks 2 pts ; responsable 1 dans Chord 1 pt."
    }
  ],
  "labs": [
    {
      "title": "1 · Préparer et dessiner",
      "action": "Reprendre l’environnement et le type de répartiteur indiqués par l’enseignant. Dessiner client → frontend du répartiteur → backends VM ; ajouter réseau, port de service et health check. Pour une réalisation cloud, vérifier projet, droits, quotas et coût avant création.",
      "proof": "Schéma légendé, rôle de chaque composant et liste des ressources prévues.",
      "question": "Pourquoi un load balancer n’est-il pas une base répliquée ?"
    },
    {
      "title": "2 · Servir une page sur une VM",
      "action": "Créer une VM selon les consignes du TP, installer/démarrer un service HTTP et afficher un identifiant de backend dans la réponse. Vérifier service local puis accès réseau autorisé ; distinguer port d’écoute, routage et pare-feu.",
      "proof": "Réponse HTTP et identité du backend ; configuration de port et règle d’accès pertinentes.",
      "question": "Le service fonctionne localement mais pas à distance : quelles couches vérifier ?"
    },
    {
      "title": "3 · Déployer plusieurs backends",
      "action": "Déployer le même service sur deux instances ou dans le groupe demandé. Configurer le backend service, le health check et le frontend du répartiteur suivant le guide adapté au produit retenu. Attendre que les backends soient sains.",
      "proof": "Identités distinctes, même version applicative, état sain de chaque backend et réponse via le frontend.",
      "question": "Pourquoi un backend qui répond en local peut-il rester marqué unhealthy ?"
    },
    {
      "title": "4 · Observer la répartition",
      "action": "Répéter des requêtes en observant l’identité du serveur et les logs. Noter la politique/affinité éventuelle. Ne pas attendre obligatoirement une alternance A/B. Augmenter la demande uniquement dans les limites de l’environnement autorisé.",
      "proof": "Petit tableau demande, backend, statut et latence ; décrire la méthode et ses limites.",
      "question": "Quelles mesures distinguent un problème de réseau d’un serveur saturé ?"
    },
    {
      "title": "5 · Provoquer une panne contrôlée",
      "action": "Dans l’environnement de TP, rendre un backend indisponible, observer les health checks et refaire les requêtes. Noter le délai de détection et d’éventuelles erreurs transitoires. Avec un groupe géré, vérifier si l’instance est automatiquement recréée ; ce mécanisme est distinct du routage. Restaurer le service.",
      "proof": "Chronologie avant/pendant/après, nombre de backends sains, erreurs et temps de réponse ; distinguer observation et hypothèse.",
      "question": "Le survivant peut-il absorber toute la demande ? Calculer λ/((n − 1)μ) dans le modèle idéal."
    },
    {
      "title": "6 · Conclure et nettoyer",
      "action": "Expliquer ce qui arrive aux sessions et aux données locales lorsqu’un backend disparaît. Proposer un stockage partagé ou une réplication adaptée selon les besoins. Après le TP, supprimer les ressources créées suivant les consignes et vérifier les ressources restantes : VM, disques, IP, répartiteur et composants associés.",
      "proof": "Conclusion sur disponibilité, cohérence et capacité ; liste des ressources supprimées/restantes. Une VM arrêtée ne signifie pas que tous les composants cessent d’être facturés.",
      "question": "Pourquoi le test de panne de deux serveurs HTTP ne démontre-t-il pas la résilience de toute l’application ?"
    }
  ],
  "book": {
    "title": "Maarten van Steen et Andrew S. Tanenbaum — Distributed Systems, 4e édition, 2023",
    "url": "https://www.distributed-systems.net/index.php/books/ds4/",
    "text": "Référence explicitement citée par le professeur p. 3 et 41. La page officielle donne accès aux diapositives et à une demande de copie numérique gratuite personnalisée. Aperçu thématique fondé sur le sommaire et les slides officiels, pas résumé d’une lecture intégrale du livre.",
    "chapters": [
      "1 Introduction : objectifs et limites de la distribution.",
      "2 Architectures : couches, services, événements et P2P.",
      "3 Processus : unités d’exécution, threads et virtualisation.",
      "4 Communication : échanges distants et messages.",
      "5 Coordination : organisation des actions concurrentes.",
      "6 Nommage : retrouver les entités et leurs ressources.",
      "7 Cohérence et réplication : garanties entre plusieurs copies.",
      "8 Tolérance aux pannes : détecter, masquer et récupérer.",
      "9 Sécurité : authentification, accès et protection des échanges."
    ],
    "reading": "Commencer par les chapitres 1 et 2 correspondant au PDF fourni. Les autres chapitres sont une carte du livre à approfondir au rythme des prochaines séances, pas un programme d’examen confirmé."
  },
  "sources": [
    {
      "title": "Support principal",
      "detail": "Olivier Grunder, Cloud et traitements distribués, fichier lucc01-cours01-26.pdf, 42 pages. Les références p. n sont les pages du PDF, couverture comprise."
    },
    {
      "title": "Notes personnelles et oral",
      "detail": "notes de cours.docx et transcription Plaud du 23/10/2026, 75 pages. Les repères hh:mm:ss renvoient à l’enregistrement. Le calendrier reste à confirmer ; les apartés privés sont exclus."
    },
    {
      "title": "Résumé Plaud et productions précédentes",
      "detail": "Résumé Plaud du 23/10 vérifié, Fiche 01 et Atelier Cloud. Noms corrigés : Maarten van Steen et Plouin (2022). Le récap Plaud du 24/10 n’a pas encore été reçu ; il complétera la partie événements et espaces partagés."
    },
    {
      "title": "Livre et ressources officielles",
      "detail": "van Steen et Tanenbaum, Distributed Systems, 4e éd., 2023 ; sommaire et diapositives officielles consultés.",
      "url": "https://www.distributed-systems.net/index.php/books/ds4/"
    },
    {
      "title": "HTTP : sémantique des méthodes",
      "detail": "RFC 9110, sections 9.3.3 (POST) et 9.3.4 (PUT), pour préciser les simplifications du support.",
      "url": "https://www.rfc-editor.org/rfc/rfc9110.html#section-9.3"
    },
    {
      "title": "TP : création de VM",
      "detail": "Documentation officielle Google Cloud consultée le 24/10/2026. Adapter les étapes aux consignes de l’enseignant.",
      "url": "https://docs.cloud.google.com/compute/docs/instances/create-start-instance"
    },
    {
      "title": "TP : exemple de répartiteur",
      "detail": "Exemple officiel de classic Application Load Balancer avec groupe géré ; exemple de préparation, pas le produit imposé pour le TP.",
      "url": "https://docs.cloud.google.com/load-balancing/docs/https/ext-https-lb-simple"
    },
    {
      "title": "Complément : conteneurs et Docker",
      "detail": "Documentation officielle : images, conteneurs et partage du noyau. Complément au support fourni, consulté le 24/10/2026.",
      "url": "https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/"
    },
    {
      "title": "Complément : microservices",
      "detail": "Microsoft Azure Architecture Center : autonomie métier, déploiement et compromis. Complément pédagogique, pas une annonce de programme d’examen.",
      "url": "https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/microservices"
    },
    {
      "title": "Complément : durée de vie des événements",
      "detail": "Redis Pub/Sub : messages manqués non rejoués ; les garanties dépendent du mécanisme choisi.",
      "url": "https://redis.io/docs/latest/develop/pubsub/"
    }
  ]
};
