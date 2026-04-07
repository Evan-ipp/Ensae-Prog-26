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
   
    def shortest_path(self, start, end, heuristique=None):
        """
        Algorithme A* (ou Dijkstra si heuristique est None) avec Pruning de Pareto.
        """
        # Si on ne donne pas d'heuristique (Dijkstra classique), on crée une 
        # fausse fonction qui renvoie toujours 0.
        if heuristique is None:
            def h_nulle(noeud):
                return 0
            heuristique = h_nulle

        d = {}
        d[start] = 0
        
        # La file contient maintenant (f_score, vraie_distance, u)
        # Au départ, f_score = 0 + h(start)
        f_start = 0 + heuristique(start)
        pq = [(f_start, 0, start)]
        
        fatigue_min_visitee = {}

        while len(pq) > 0:
            # On extrait les 3 éléments de la file
            f_u, dist_u, u = heapq.heappop(pq)

            if isinstance(u, tuple):
                noeud = u[0]
                fatigue = u[1]
                
                # On applique le pruning
                if noeud in fatigue_min_visitee and fatigue >= fatigue_min_visitee[noeud]:
                    continue
                fatigue_min_visitee[noeud] = fatigue
            else:
                noeud = u

            if noeud == end:
                return dist_u 

            if u in d and dist_u > d[u]:
                continue

            for voisin in self.neighbours(u):
                v = voisin[0]
                poids = voisin[1]

                nouvelle_dist = dist_u + poids

                if v not in d or nouvelle_dist < d[v]:
                    d[v] = nouvelle_dist
                    
                    if isinstance(v, tuple):
                        nom_ville_voisin = v[0]
                    else:
                        nom_ville_voisin = v
                        
                    # f(n) = g(n) + h(n)
                    f_score = nouvelle_dist + heuristique(nom_ville_voisin)
                    
                    # On ajoute le triplet dans la file
                    heapq.heappush(pq, (f_score, nouvelle_dist, v))

        return np.inf

import heapq

def creer_heuristique(network, end_node):
    """
    Crée une fonction heuristique admissible pour A*.
    Elle pré-calcule la distance la plus courte (sans fatigue) depuis 
    chaque nœud vers le nœud de fin en effectuant un Dijkstra sur le graphe inversé.
    """
    # 1. Construction du graphe inversé (on ignore la fatigue)
    graphe_inverse = {}
    
    # Initialisation des clés pour éviter les KeyError
    for u in network._roads.keys():
        if u not in graphe_inverse:
            graphe_inverse[u] = []
            
    for u, voisins in network._roads.items():
        for v, longueur, f in voisins:
            if v not in graphe_inverse:
                graphe_inverse[v] = []
            # On inverse le sens de l'arête : v -> u
            graphe_inverse[v].append((u, longueur))
            
    # 2. Dijkstra classique depuis end_node sur le graphe inversé
    distances = {noeud: float('inf') for noeud in graphe_inverse}
    if end_node in distances:
        distances[end_node] = 0
        
    pq = [(0, end_node)]
    
    while pq:
        dist_u, u = heapq.heappop(pq)
        
        if dist_u > distances[u]:
            continue
            
        for voisin, poids in graphe_inverse[u]:
            nouvelle_dist = dist_u + poids
            if nouvelle_dist < distances[voisin]:
                distances[voisin] = nouvelle_dist
                heapq.heappush(pq, (nouvelle_dist, voisin))
                
    def heuristique(noeud):
        # Si le nœud est déconnecté du point d'arrivée, on renvoie 0 par sécurité
        # pour retomber sur un comportement de type Dijkstra classique.
        return distances.get(noeud, 0)
        
    return heuristique

class GraphImplicit(Graph):
    """
    Sous classe de Graph permettant de générer un graphe avec uniquement les voisins visités lors du parcours.
    """
    def __init__(self, fonction_voisins):
        self.fonction_voisins = fonction_voisins

    def neighbours(self, node):
        return self.fonction_voisins(node)



