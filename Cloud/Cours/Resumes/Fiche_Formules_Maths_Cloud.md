# Fiche de formules · Cloud

> Master DSICS · Écrit de mi-décembre · Supports disponibles au 14 novembre 2026

Les références C1 et C2 désignent les pages des PDF d’Olivier Grunder, couverture comprise. Les relations dérivées et les modèles d’entraînement précisent leurs hypothèses. Le périmètre exact de l’écrit et les apports de la séance du 14 novembre restent à confirmer.

## 1 · File d’attente M/M/1 et loi de Little

**Quand l’utiliser.** Un serveur, arrivées de Poisson à taux λ, temps de service exponentiels indépendants de moyenne S, file sans limite. En régime stationnaire, il faut λ < μ. Convertir les millisecondes en secondes avant d’inverser S.

| Cherché | Formule et lecture |
| --- | --- |
| Capacité et utilisation | **μ = 1/S** en req/s. **ρ = U = λ/μ = λS**. Occupation en % = 100U. |
| Exactement k requêtes dans le système | **pₖ = (1 − U)Uᵏ**, k ≥ 0. Donc **p₀ = 1 − U** et **P(K ≥ k) = Uᵏ**. Pour retrouver pₖ, partir de λpₖ = μpₖ₊₁ et normaliser la somme des probabilités à 1. |
| Débit moyen et nombre moyen dans le système | **X = μU = λ**. **L = U/(1 − U)**. Le cours note aussi N ce nombre moyen. Il inclut le service et la file. |
| Temps de réponse, attente et longueur de la file | **R = S/(1 − U) = 1/(μ − λ)**. **R/S = 1/(1 − U)**. **Wq = R − S**, **Lq = λWq = U²/(1 − U)**. |
| Loi de Little | **L = XR**, et **Lq = XWq** pour la file seule. Utiliser le même périmètre, des unités compatibles et des moyennes stables. La loi s’applique aussi au-delà de M/M/1. |

**Exemple.** λ = 80 req/s et S = 10 ms. μ = 100 req/s, U = 0,8, L = 4, R = 50 ms et Wq = 40 ms. Exactement deux demandes : p₂ = 0,2 × 0,8² = 12,8 %. Au moins deux : 64 %.

## 2 · Dimensionner des serveurs identiques

| Situation | Relation sous répartition uniforme |
| --- | --- |
| n serveurs et charge totale Λ | **λᵢ = Λ/n** et **U = Λ/(nμ)**. Pour n files M/M/1 indépendantes, **Rᵢ = 1/(μ − Λ/n)** si Λ/n < μ. |
| Occupation maximale Umax | **nmin = max(1, plafond(Λ/(Umax·μ)))**, avec 0 < Umax < 1. Pour une réponse cible Rmax > 0, il faut **λᵢ ≤ μ − 1/Rmax**. Si la charge totale est positive, une cible Rmax ≤ S est impossible avec ce modèle. |
| f pannes détectées, n > f | **U = Λ/((n − f)μ)**. Pour tenir Umax avec f pannes, dimensionner les survivants à nmin et prévoir **nmin + f** serveurs. |

**Exemple.** Λ = 210 req/s, μ = 100 req/s et Umax = 0,70. Trois serveurs en fonctionnement, quatre au total pour tenir la cible après une panne. Avec trois serveurs au total et une panne, U = 1,05. Une file unique alimentant plusieurs serveurs relève d’un autre modèle de latence.

Sources · C1 p. 16 à 18 et Plaud 23/10 p. 8 à 9. Little par périmètre et le dimensionnement sont des applications du modèle.

<!-- page -->

# Migration Cloud et recherche pair-à-pair

## 3 · Coûts et flux de migration

| Cherché | Formule et conditions |
| --- | --- |
| Bénéfice forfaitaire sur une période | **B = Bc·Mc + Bs·Ms**. Bc et Bs sont les bénéfices unitaires du calcul et du stockage. Mc et Ms sont les nombres de composants migrés. |
| Fraction migrée d’un composant i | **fᵢ = nᵢ/Nᵢ**. nᵢ serveurs migrés sur Nᵢ serveurs. Part locale = 1 − fᵢ. Le modèle suppose une distribution de trafic homogène et des destinations indépendantes des origines. |
| Transactions i → j après migration | Multiplier Tᵢⱼ par la part du départ et celle de l’arrivée. **Local → local** (1 − fᵢ)(1 − fⱼ). **Local → cloud** (1 − fᵢ)fⱼ. **Cloud → local** fᵢ(1 − fⱼ). **Cloud → cloud** fᵢfⱼ. La somme des parts vaut 1. |
| Trafic et coût | **Vᵢⱼ = Tᵢⱼ·sᵢⱼ** si sᵢⱼ est un volume par transaction. Avec les usagers, additionner réception et émission, Σᵢ(Tu,i·su,i + Ti,u·si,u). Répartir ces flux avec 1 − fᵢ et fᵢ selon l’emplacement du serveur. **Coût réseau = Σ(volume du flux × tarif unitaire applicable)**. |
| Économie nette | **Économie = coût avant − coût après**, à horizon identique. Si on part d’un gain forfaitaire hors réseau, déduire **coût réseau après − coût réseau avant**, ainsi que les surcoûts éventuels absents du forfait. |

**Exemple.** fᵢ = 25 %, fⱼ = 50 %, Tᵢⱼ = 800 transactions/jour et sᵢⱼ = 0,02 Go/transaction. Local → cloud = 0,75 × 0,50 × 800 = 300 transactions/jour, soit 6 Go/jour. À 0,10 €/Go, cela fait 0,60 €/jour pour ce flux. Si Sᵢⱼ est déjà exprimé en Go/jour dans l’énoncé, le volume est déjà agrégé. Vérifie les unités avant toute multiplication.

## 4 · Compter les liens et chercher une donnée

| Sujet | Formule ou méthode |
| --- | --- |
| Adaptateurs EAI | **N(N − 1)** en point-à-point orienté, **N(N − 1)/2** en paires non orientées. Avec un broker distinct, **2N** directions ou N liens bidirectionnels. Avec N = 6, cela donne 30 contre 12 dans la convention orientée. |
| Hypercube de dimension d | **2ᵈ** nœuds, **d** voisins par nœud, **d·2ᵈ⁻¹** liens physiques non orientés. Sauts minimaux = bits différents, soit distance de Hamming. De 0 à 14 en dimension 4 : trois sauts. |
| Chord | Espace circulaire de **2ᵐ** identifiants, nœuds présents éventuellement moins nombreux. Responsable = **succ(k)**, le premier nœud à partir de k inclus dans le sens croissant (revenir au début). Entrée de raccourci j du nœud n = succ((n + 2ʲ) mod 2ᵐ), j de 0 à m − 1. |
| Marche aléatoire idéalisée | N nœuds, r copies, **p = r/N**. Tirages indépendants uniformes avec remise. **P(K = k) = p(1 − p)ᵏ⁻¹**, **P(K ≤ k) = 1 − (1 − p)ᵏ**, **E[K] = 1/p = N/r** sans limite de tirages. Sur un vrai graphe, les visites peuvent être dépendantes. |
| Inondation idéalisée | Degré d et voisinage sans recouvrement. Frontière du saut k ≥ 1 : **F(k) = d(d − 1)ᵏ⁻¹**. Cumul hors source = Σⱼ F(j), j de 1 à k. Une espérance de copies **F(k)·r/N ≥ 1** indique un ordre de grandeur. Le résultat peut manquer malgré ce seuil. |

Sources · C1 p. 21 à 22, 32 et 34 à 37. Plaud 24/10 p. 5 à 6. La règle des raccourcis Chord et les probabilités cumulées complètent les exemples du support.

<!-- page -->

# Threads, multicast et gossip

## 5 · TLP et coût de diffusion

| Cherché | Formule / mode de calcul |
| --- | --- |
| TLP · Parallélisme des threads | **TLP = Σᵢ(i·cᵢ)/(1 − c₀)** pour i = 1 à N. cᵢ = fraction du temps avec exactement i threads qui s’exécutent simultanément. Σcᵢ = 1. Si c₀ = 1, le TLP est indéfini. Exemple avec c₀ = 0,2, c₁ = 0,5, c₂ = 0,3 : **1,375**. |
| Stress d’un lien physique | **Nombre de traversées du lien** par les copies du message. Dérouler chaque lien logique en chemin physique. Compter toutes les copies qui passent sur le lien demandé. |
| Élongation (stretch) | **Délai du chemin via l’overlay / délai du plus court chemin physique**, pour les mêmes extrémités. Dans l’exemple C2 p. 39 avec liens bidirectionnels et délais additifs, A → B → E → D → C coûte 82, le plus court A → C coûte 52, soit **82/52 ≈ 1,58**. Le lien Ra–Rb est emprunté deux fois sur ce trajet logique. |

## 6 · Anti-entropie · Qui reste ignorant après un tour ?

N = population, p = fraction ignorante au début du tour. Le modèle de calcul suppose des choix aléatoires indépendants uniformes avec remise et un état de départ figé pendant le tour. Pour une cible donnée, (1 − 1/N) est la probabilité qu’un initiateur ne la choisisse pas.

| Stratégie | Probabilité qu’un nœud quelconque soit encore ignorant au tour suivant |
| --- | --- |
| Pull | **p′ = p²**. Il était ignorant (p) et a interrogé un pair ignorant (p). |
| Push | **p′ = p(1 − 1/N)ᴺ⁽¹⁻ᵖ⁾**. Il était ignorant et aucun des N(1 − p) initiateurs informés ne l’a choisi. Pour N grand, **p′ ≈ p exp(−(1 − p))**. Si p est aussi petit, **p′ ≈ p/e**. |
| Push-pull | **p′ = p²(1 − 1/N)ᴺ⁽¹⁻ᵖ⁾** avec les mêmes tirages indépendants. Il était ignorant, son pull ne l’a pas informé et aucun push ne l’a atteint. Pour N grand, **p′ ≈ p² exp(−(1 − p))**. Le support donne O(log N) tours dans son modèle. |

**Exemple avec N = 10, p = 0,60.** Pull : 36 %. Push : 0,60 × 0,9⁴ ≈ 39,37 %. Push-pull : 0,36 × 0,9⁴ ≈ 23,62 %. La ligne push-pull et le classement push/pull du support C2 p. 40 sont ambigus ou incohérents avec ses récurrences dans certains régimes. Justifier la formule par les événements et préciser le modèle de tirage.

## 7 · Compléments figurant dans les supports

| Sujet | Relation et interprétation |
| --- | --- |
| Rumeur avec arrêt · C2 p. 40 à 41 | **s = exp(−(1 + 1/pstop)(1 − s))**. s est la fraction ignorante finale, pstop la probabilité d’arrêter après un contact déjà informé. Retenir la solution non triviale 0 < s < 1 pour le modèle démarré avec une source dans une grande population. Répliques ignorantes ≈ N·s. Pour pstop = 1, s ≈ 0,203. |
| Dérivation de la rumeur · C2 p. 40 à 41 | Avec s ignorants et i informés actifs, **ds/dt = −s·i**, **di/dt = s·i − pstop(1 − s)i**. Leur quotient donne **di/ds = −(1 + pstop) + pstop/s**. Avec i(1) ≈ 0, **i(s) = (1 + pstop)(1 − s) + pstop ln(s)**. Poser i(s) = 0 à la fin donne l’équation précédente. |
| Capteurs et communautés · C1 p. 25 à 26 | **τ = Tactif/(Tactif + Tsuspendu)**. Ex. 2 s sur un cycle de 10 s → 20 %. Mobilité, si Fⱼ est non vide : ajouter j à Cᵢ si **card(Fⱼ ∩ Cᵢ)/card(Fⱼ) > λ**. Fusion si **card(Cᵢ ∩ Cⱼ) > γ·card(Cᵢ ∪ Cⱼ)**. Ici λ et γ sont des seuils. |

Sources · C2 p. 13 et 38 à 41. Plaud 24/10 signale une possible exclusion de schémas avancés de mobilité et de capteurs. À vérifier avant d’écarter cette partie.
