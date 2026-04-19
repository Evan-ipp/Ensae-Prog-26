import sys 
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

NET_DIR = ROOT / "examples"

import unittest 
from network import Network
from graph import creer_heuristiques

class Test_NetworkAndAlgorithms(unittest.TestCase):
    
    def setUp(self):
        """
        Cette methode est appelee avant chaque test. 
        Elle permet de charger le graphe une seule fois.
        """
        self.network = Network.from_file(NET_DIR / "small.txt")

    def test_network_loading(self):
        """Test le bon chargement des routes et du depart/arrivee."""
        self.assertEqual(self.network.start, "lozere")
        self.assertEqual(self.network.end, "saclay")
        self.assertEqual(self.network._roads, {
            'lozere': [('ensae', 10, 2), ('guichet', 20, 0)], 
            'ensae': [('saclay', 45, 0)], 
            'guichet': [('ensae', 15, 1)],
            'saclay': []
        })

    def test_graphe_etendu_shortest_path(self):
        """Test l'algorithme de base sur le graphe etendu statique."""
        g_extended = self.network.build_extended_graph()
        resultat = g_extended.shortest_path((self.network.start, 0), self.network.end)
        self.assertEqual(resultat, 125)

    def test_graphe_implicite_dijkstra(self):
        """Test l'algorithme Dijkstra sur le graphe implicite (sans heuristique)."""
        g_implicite = self.network.build_implicit_graph()
        resultat = g_implicite.shortest_path((self.network.start, 0), self.network.end)
        self.assertEqual(resultat, 125)

    def test_graphe_implicite_astar(self):
        """Test l'algorithme A* avec les deux heuristiques (Simple et Fatigue)."""
        g_implicite = self.network.build_implicit_graph()
        h_simple, h_fatigue = creer_heuristiques(self.network, self.network.end)
        
        # Test avec H1
        res_h1 = g_implicite.shortest_path((self.network.start, 0), self.network.end, heuristique=h_simple)
        self.assertEqual(res_h1, 125)
        
        # Test avec H2
        res_h2 = g_implicite.shortest_path((self.network.start, 0), self.network.end, heuristique=h_fatigue)
        self.assertEqual(res_h2, 125)

    def test_extension1_ordre_impose(self):
        """Test l'extension multi-missions avec ordre impose."""
        missions = [('lozere', 'guichet'), ('ensae', 'saclay')]
        g_multi, cibles = self.network.construire_graphe_missions_ordonnees(missions)
        
        start_node = missions[0][0]
        etape_depart = 0
        while etape_depart < len(cibles) and start_node == cibles[etape_depart]:
            etape_depart += 1
            
        etat_initial = ((start_node, etape_depart), 0)
        etat_final = (cibles[-1], len(cibles))
        
        cout = g_multi.shortest_path(etat_initial, etat_final)
        self.assertEqual(cout, 125)

    def test_extension1_ordre_libre(self):
        """Test l'extension multi-missions avec ordre libre."""
        missions = [('lozere', 'guichet'), ('ensae', 'saclay')]
        g_multi = self.network.construire_graphe_missions_libres(missions)
        
        etat_initial = ((missions[0][0], frozenset(), -1), 0)
        cout = g_multi.shortest_path(etat_initial, "etat final")
        self.assertEqual(cout, 125)

if __name__ == '__main__':
    unittest.main()