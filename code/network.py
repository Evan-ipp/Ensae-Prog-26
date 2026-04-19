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
            return voisins

        from graph import GraphImplicit
        return GraphImplicit(generer_voisins), cibles

    def construire_graphe_missions_libres(self, missions):
        """
        Construit un graphe implicite pour des missions multiples sans ordre impose.
        L'agent doit accomplir toutes les missions, mais l'algorithme determine l'ordre optimal.
        """
        nb_missions = len(missions)
        
        def generer_voisins(etat):
            # etat = (noeud_logique, fatigue_accumulee)
            noeud_logique, fa = etat[0], etat[1]
            
            # Gestion de la condition d'arret
            if noeud_logique == "etat final":
                return []
                
            ville_actuelle = noeud_logique[0]
            accomplies = noeud_logique[1] # frozenset des indices de missions terminees
            en_cours = noeud_logique[2]    # index de la mission actuelle ou -1 si libre
            
            voisins = []
            
            # 1. Condition de victoire globale
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
                        nouvel_etat_logique = (ville_actuelle, accomplies, i)
                        voisins.append(((nouvel_etat_logique, fa), 0))
                        
            # 3. Possibilite de terminer la mission en cours
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
                    nouvel_etat_logique = (v, accomplies, en_cours)
                    voisins.append(((nouvel_etat_logique, nouvelle_fatigue), cout))
                    
            return voisins

        from graph import GraphImplicit
        return GraphImplicit(generer_voisins)