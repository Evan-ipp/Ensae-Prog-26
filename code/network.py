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
        edges = {}
        for u in self._roads.keys():
            edges[u] = []
            for e in self._roads[u]:
                v = e[0]
                longueur = e[1]
                edges[u].append((v, longueur))
        return Graph(edges)

    def build_extended_graph(self):
        # 1. Calcul de la fatigue maximale avec des boucles classiques
        fm = 0
        for u in self._roads.keys():
            for e in self._roads[u]:
                fatigue = e[2]
                fm = fm + fatigue

        # 2. Construction du dictionnaire
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