from graph import *

class Network:
    """
    Class for a network that represents the environment (with length and fatigue on roads). 
    """

    def __init__(self, roads={}, start=None, end=None):
        self._roads = roads
        self.start = start
        self.end = end

    def __str__(self): 
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
        edges = {}
        for u in self._roads.keys():
            edges[u] = []
            for e in self._roads[u]:
                v = e[0]
                longueur = e[1]
                edges[u].append((v, longueur))
        return Graph(edges)

    def build_extended_graph(self):
        fm = 0
        for u in self._roads.keys():
            for e in self._roads[u]:
                fa = e[2]
                fm = fm + fa

        routes_etendues = {}
        for u in self._roads.keys():
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
        L'agent doit accomplir les missions dans l'ordre : s1 -> t1, puis s2 -> t2, etc.
        """
        cibles = []
        for s, t in missions:
            cibles.append(s)
            cibles.append(t)
            
        def generer_voisins(etat):
            noeud_logique, fa = etat[0], etat[1]
            ville_actuelle, etape = noeud_logique[0], noeud_logique[1]
            
            voisins = []
            
            prochaine_etape = etape
            while prochaine_etape < len(cibles) and ville_actuelle == cibles[prochaine_etape]:
                prochaine_etape += 1
            
            if prochaine_etape != etape:
                voisins.append((((ville_actuelle, prochaine_etape), fa), 0))
                return voisins

            if ville_actuelle in self._roads:
                for v, longueur, f in self._roads[ville_actuelle]:
                    nouvelle_fatigue = fa + f
                    cout = longueur * (1 + fa)
                    voisins.append((((v, etape), nouvelle_fatigue), cout))
            return voisins

        from graph import GraphImplicit
        return GraphImplicit(generer_voisins), cibles

    def construire_graphe_missions_libres(self, missions):
        """
        Construit un graphe implicite pour des missions multiples sans ordre impose.
        L'algorithme teste toutes les combinaisons implicitement pour trouver l'ordre optimal.
        """
        nb_missions = len(missions)
        # Etat final "deguise" pour eviter l'erreur TypeError dans heapq
        noeud_final_logique = ("ZZZ_FIN", frozenset(), -1)
        
        def generer_voisins(etat):
            noeud_logique, fa = etat[0], etat[1]
            
            # Securite : la fin du graphe ne s'etend plus
            if noeud_logique == noeud_final_logique:
                return []
                
            ville_actuelle = noeud_logique[0]
            accomplies = noeud_logique[1]  
            en_cours = noeud_logique[2]    
            
            voisins = []
            
            # REGLE 1 : Condition de victoire
            if len(accomplies) == nb_missions:
                voisins.append(((noeud_final_logique, fa), 0))
                return voisins

            # REGLE 2 : Demarrer une nouvelle mission
            if en_cours == -1:
                for i, (s, t) in enumerate(missions):
                    if i not in accomplies and ville_actuelle == s:
                        nouvel_etat_logique = (ville_actuelle, accomplies, i)
                        voisins.append(((nouvel_etat_logique, fa), 0))
                        
            # REGLE 3 : Terminer la mission en cours
            if en_cours != -1:
                s, t = missions[en_cours]
                if ville_actuelle == t:
                    nouvelles_accomplies = accomplies.union(frozenset([en_cours]))
                    nouvel_etat_logique = (ville_actuelle, nouvelles_accomplies, -1)
                    voisins.append(((nouvel_etat_logique, fa), 0))
                    
            # REGLE 4 : Deplacements physiques normaux
            if ville_actuelle in self._roads:
                for v, longueur, f in self._roads[ville_actuelle]:
                    nouvelle_fatigue = fa + f
                    cout = longueur * (1 + fa)
                    nouvel_etat_logique = (v, accomplies, en_cours)
                    voisins.append(((nouvel_etat_logique, nouvelle_fatigue), cout))
                    
            return voisins

        from graph import GraphImplicit
        return GraphImplicit(generer_voisins)