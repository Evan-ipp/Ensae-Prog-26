"""
This is the graph module. It contains the classes Graph and GraphImplicit
"""
import numpy as np
import heapq

class Graph:
    """
    A minimal class for directed weighted graph represented as adjacency list. 
    
    Attributes: 
    -----------
    edges: dict
        A dictionary that contains the list of neighbors of each node with its weight.
        Ex: edges = {v0: [(v1, 21), (v2, 12)], 
                     v1: [(v0, 74), (v2, 32)], 
                     ...}

    Methods: 
    --------
    neighbours(self, node): 
        Returns the list of all neighbors of a node
    """

    def __init__(self, edges):
        self._edges = edges

    def neighbours(self, node):
        if node not in self._edges:
            return []
        return self._edges[node]
   
    def shortest_path(self, start, end):
        """
        On applique l'algorithme de dijsktra avec une file de priorité.
        La complexité est en :
        Q1.1 : O(E * log(V))
        Q1.2 : O(E*Fm * log(V*Fm)) car le graphe etendu possede V*Fm noeuds et E*Fm aretes.
        """
        d = {}
        d[start] = 0
        pq = [(0, start)]

        while len(pq) > 0:
            dist_u, u = heapq.heappop(pq)

            # On vérifie si on est dans le cas du graphe simple ou du graphe étendu
            if isinstance(u, tuple):
                noeud = u[0]
            else:
                noeud = u

            if noeud == end:
                return dist_u

            # Si le noeud a déjà été visité avec un meilleur temps, on l'ignore
            if u in d and dist_u > d[u]:
                continue

            for voisin in self.neighbours(u):
                v = voisin[0]
                poids = voisin[1]

                nouvelle_dist = dist_u + poids

                # Si le voisin n'est pas encore dans d, ou si on a trouvé un meilleur chemin
                if v not in d or nouvelle_dist < d[v]:
                    d[v] = nouvelle_dist
                    heapq.heappush(pq, (nouvelle_dist, v))

        return np.inf
 

class GraphImplicit(Graph):
    """
    Sous classe de Graph permettant de générer un graphe avec uniquement les voisins visités lors du parcours.
    """
    def __init__(self, fonction_voisins):
        self.fonction_voisins = fonction_voisins

    def neighbours(self, node):
        return self.fonction_voisins(node)
