"""
This is the graph module. It contains the classes Graph and GraphImplicit
"""
import numpy as np

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

    def shortest_path(self):
        d = [np.inf for i in range(len(self._edges))]
        visited = [False for i in range(len(self._edges))]
        d[0] = 0

        for i in range(len(self._edges)):
            visited[i] = True
            suiv = self._edges[i]
            #voisin(num, distance)
            for voisin in suiv:   
                if not visited[voisin[0]]:
                    if d[voisin[0]] > d[i]+voisin[1]:
                        d[voisin[0]] = d[i]+voisin[1]
        return d




https://github.com/Evan-ipp/Ensae-Prog-26


