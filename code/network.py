from graph import *

class Network:
    """
    Class for a network that represents the environment (with length and fatigue on roads). 
    """

    def __init__(self, roads={}, start=None, end=None):
        """
        Initializes the network from a dictionary roads. 

        Parameters: 
        -----------
        roads: dict
            A dictionary of the roads as an adjacency list, that is 
            roads[u] = list of (v, length, fatigue)
            Ex: roads = {v0: [(v1, 21, 2), (v2, 12, 4)], 
                        v1: [(v0, 74, 2), (v2, 32, 1)], 
                        ...}
        start, end: 
            Start and end nodes added as attributes
        """
        self._roads = roads
        self.start = start
        self.end = end

    def __str__(self): 
        """
        Prints the network as text.
        """
        output = f"A network with {len(self._roads)} nodes and the following adjacency list:\n"
        return output+self._roads.__str__()

    @classmethod
    def from_file(cls, filename: str):
        roads = {}
        with open(filename, "r") as testcase:
            nb, start, end = testcase.readline().strip().split()
            for _ in range(int(nb)):
                i, j, l, f = testcase.readline().strip().split()
                l, f = int(l), int(f)

                if i not in roads:
                    roads[i] = []
                roads[i].append((j, l, f))

                if j not in roads:
                    roads[j] = []

        return cls(roads=roads, start=start, end=end)

    def build_simple_graph(self):
        """
        Construit un graphe simple
        """
        edges = {}
        for u in self._roads.keys():
            edges[u] = []
            for e in self._roads[u]:
                v = e[0]
                longueur = e[1]
                edges[u].append((v, longueur))
        return Graph(edges)

    def build_extended_graph(self):
        """
        Construit un graphe etendu
        """
        # Calcul de la fatigue maximale possible
        fm = 0
        for u in self._roads.keys():
            for e in self._roads[u]:
                fa = e[2]
                fm = fm + fa

        # Construction du dictionnaire du graphe
        routes_etendues = {}
        for u in self._roads.keys():
            # On duplique chaque noeud fm+1 fois
            for fa in range(fm + 1):
                routes_etendues[(u, fa)] = []

                for e in self._roads[u]:
                    v = e[0]
                    longueur = e[1]
                    f = e[2]

                    fs = fa + f
                    if fs <= fm:
                        routes_etendues[(u, fa)].append(((v, fs), longueur * (1 + fa)))

        return Graph(routes_etendues)

    def build_implicit_graph(self):
        """
        Construit un graphe implicite
        """
        def generer_voisins(etat):
            u = etat[0]
            fa = etat[1]
            voisins = []

            if u in self._roads:
                for e in self._roads[u]:
                    v = e[0]
                    longueur = e[1]
                    f = e[2]

                    nouvel_etat = (v, fa + f)
                    voisins.append((nouvel_etat, longueur * (1 + fa)))

            return voisins

        return GraphImplicit(generer_voisins)

<<<<<<< HEAD
    def construire_graphe_missions_ordonnees(self, missions):
        """
        Construit un graphe implicite pour des missions multiples avec un ordre impose.
        L'agent doit accomplir les missions dans l'ordre : v1s -> v1t, puis v2s -> v2t, etc.
        """
        # On cree une liste plate des points de passage obligatoires : [s1, t1, s2, t2, ...]
        cibles = []
        for s, t in missions:
            cibles.append(s)
            cibles.append(t)
            
        def generer_voisins(etat):
            # etat = (noeud_logique, fatigue_accumulee)
            # noeud_logique = (ville_actuelle, etape_dans_la_liste_cibles)
            noeud_logique, fa = etat[0], etat[1]
            ville_actuelle, etape = noeud_logique[0], noeud_logique[1]
            
            voisins = []
            
            # Validation automatique des etapes si on est deja sur la ville cible
            prochaine_etape = etape
            while prochaine_etape < len(cibles) and ville_actuelle == cibles[prochaine_etape]:
                prochaine_etape += 1
            
            # Si on a progresse dans les etapes (on a valide une cible), transition gratuite
            if prochaine_etape != etape:
                voisins.append((((ville_actuelle, prochaine_etape), fa), 0))
                return voisins

            # Deplacements physiques normaux sur le reseau routier
            if ville_actuelle in self._roads:
                for v, longueur, f in self._roads[ville_actuelle]:
                    nouvelle_fatigue = fa + f
                    cout = longueur * (1 + fa)
                    # On reste a la meme etape de mission tant qu'on n'a pas atteint la cible
                    voisins.append((((v, etape), nouvelle_fatigue), cout))
=======
    def build_multimission_implicit_graph(self, missions):
        """
        Construit un graphe implicite pour le cas de multiples missions ordonnees.
        
        Parametres:
        -----------
        missions : list of tuples
            Liste des missions sous la forme [(depart_1, arrivee_1), (depart_2, arrivee_2), ...]
            
        Retourne:
        ---------
        Un objet GraphImplicit et la liste des cibles successives a atteindre.
        """
        if not missions:
            raise ValueError("La liste des missions ne peut pas etre vide.")

        # Construction de la liste chronologique des points de passage obligatoires.
        # L'agent commence a depart_1. Il doit atteindre arrivee_1, puis depart_2, arrivee_2, etc.
        cibles = []
        for i, (s, t) in enumerate(missions):
            if i > 0:
                cibles.append(s)
            cibles.append(t)
            
        nb_cibles = len(cibles)
        
        def generer_voisins(etat):
            # Dans ce graphe, l'etat est un tuple : ((ville, etape), fatigue)
            n_e = etat[0]
            ville_actuelle = n_e[0]
            etape = n_e[1]
            fa = etat[1]
            
            voisins = []
            
            # Si toutes les cibles sont atteintes, on arrete l'exploration de cette branche
            if etape == nb_cibles:
                return voisins
                
            if ville_actuelle in self._roads:
                for e in self._roads[ville_actuelle]:
                    v = e[0]
                    longueur = e[1]
                    f = e[2]
                    
                    nouvelle_fatigue = fa + f
                    cout = longueur * (1 + fa)
                    
                    # Verification : a-t-on atteint la cible attendue pour l'etape courante ?
                    nouvelle_etape = etape
                    # Boucle while au cas ou une meme ville validerait plusieurs etapes d'un coup
                    while nouvelle_etape < nb_cibles and v == cibles[nouvelle_etape]:
                        nouvelle_etape += 1
                        
                    nouvel_etat = ((v, nouvelle_etape), nouvelle_fatigue)
                    voisins.append((nouvel_etat, cout))
                    
>>>>>>> 78bd5feffe9b1b7911e07cb00d415368b67c4689
            return voisins

        from graph import GraphImplicit
        return GraphImplicit(generer_voisins), cibles
<<<<<<< HEAD

    def construire_graphe_missions_libres(self, missions):
        """
        Construit un graphe implicite pour des missions multiples sans ordre impose.
        L'agent doit accomplir toutes les missions, mais l'algorithme determine l'ordre optimal.
=======
    
    def build_free_order_multimission_graph(self, missions):
        """
        Construit un graphe implicite pour des missions multiples sans ordre impose.
        L'agent doit accomplir toutes les missions, mais l'algorithme determine 
        l'ordre optimal de lui-meme.
>>>>>>> 78bd5feffe9b1b7911e07cb00d415368b67c4689
        """
        nb_missions = len(missions)
        
        def generer_voisins(etat):
            # etat = (noeud_logique, fatigue_accumulee)
<<<<<<< HEAD
            noeud_logique, fa = etat[0], etat[1]
            
            # Gestion de la condition d'arret
            if noeud_logique == "etat final":
                return []
                
            ville_actuelle = noeud_logique[0]
            accomplies = noeud_logique[1] # frozenset des indices de missions terminees
            en_cours = noeud_logique[2]    # index de la mission actuelle ou -1 si libre
=======
            # noeud_logique = (ville_actuelle, frozenset(missions_accomplies), mission_en_cours)
            noeud_logique = etat[0]
            fa = etat[1]
            
            # Gestion de la condition d'arret : on ne s'etend plus si on est a la fin
            if noeud_logique == "ETAT_FINAL":
                return []
                
            ville_actuelle = noeud_logique[0]
            accomplies = noeud_logique[1]
            en_cours = noeud_logique[2]
>>>>>>> 78bd5feffe9b1b7911e07cb00d415368b67c4689
            
            voisins = []
            
            # 1. Condition de victoire globale
<<<<<<< HEAD
            # Si le nombre de missions accomplies est egal au total
            if len(accomplies) == nb_missions:
                # Transition vers le noeud de fin universel
                voisins.append((("etat final", fa), 0))
                return voisins

            # 2. Possibilite de commencer une nouvelle mission
            # On ne peut commencer que si on n'est pas deja en train d'en faire une
            if en_cours == -1:
                for i, (s, t) in enumerate(missions):
                    if i not in accomplies and ville_actuelle == s:
                        # On demarre la mission i
=======
            # Si toutes les missions sont dans l'ensemble 'accomplies'
            if len(accomplies) == nb_missions:
                # On cree une transition gratuite (cout 0) vers un noeud de fin universel
                voisins.append((("ETAT_FINAL", fa), 0))
                return voisins

            # 2. Possibilite de commencer une nouvelle mission
            # Condition : on ne doit pas etre deja en train de faire une mission (en_cours == -1)
            if en_cours == -1:
                for i, (s, t) in enumerate(missions):
                    if i not in accomplies and ville_actuelle == s:
                        # Transition logique : on demarre la mission (cout 0, fatigue inchangee)
>>>>>>> 78bd5feffe9b1b7911e07cb00d415368b67c4689
                        nouvel_etat_logique = (ville_actuelle, accomplies, i)
                        voisins.append(((nouvel_etat_logique, fa), 0))
                        
            # 3. Possibilite de terminer la mission en cours
<<<<<<< HEAD
            # On doit etre sur la ville destination de la mission active
            if en_cours != -1:
                s, t = missions[en_cours]
                if ville_actuelle == t:
                    # On ajoute la mission aux accomplies (utilisation de union pour eviter le |)
                    nouvelles_accomplies = accomplies.union(frozenset([en_cours]))
                    nouvel_etat_logique = (ville_actuelle, nouvelles_accomplies, -1)
                    voisins.append(((nouvel_etat_logique, fa), 0))
                    
            # 4. Deplacements physiques normaux sur le reseau
            if ville_actuelle in self._roads:
                for v, longueur, f in self._roads[ville_actuelle]:
                    nouvelle_fatigue = fa + f
                    cout = longueur * (1 + fa)
=======
            # Condition : on est sur la destination de la mission active
            if en_cours != -1:
                s, t = missions[en_cours]
                if ville_actuelle == t:
                    # On ajoute la mission aux accomplies par union d'ensembles
                    nouvelles_accomplies = accomplies | frozenset([en_cours])
                    # On redevient libre (-1)
                    nouvel_etat_logique = (ville_actuelle, nouvelles_accomplies, -1)
                    voisins.append(((nouvel_etat_logique, fa), 0))
                    
            # 4. Deplacements physiques normaux sur le reseau routier
            if ville_actuelle in self._roads:
                for e in self._roads[ville_actuelle]:
                    v = e[0]
                    longueur = e[1]
                    f = e[2]
                    
                    nouvelle_fatigue = fa + f
                    cout = longueur * (1 + fa)
                    
>>>>>>> 78bd5feffe9b1b7911e07cb00d415368b67c4689
                    nouvel_etat_logique = (v, accomplies, en_cours)
                    voisins.append(((nouvel_etat_logique, nouvelle_fatigue), cout))
                    
            return voisins

        from graph import GraphImplicit
<<<<<<< HEAD
        return GraphImplicit(generer_voisins)
=======
        return GraphImplicit(generer_voisins)
    
>>>>>>> 78bd5feffe9b1b7911e07cb00d415368b67c4689
