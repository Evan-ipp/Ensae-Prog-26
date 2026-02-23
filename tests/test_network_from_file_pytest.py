import sys 
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.append(str(ROOT / "code"))

NET_DIR = ROOT / "examples"

import pytest
from network import Network

def test_network_small():
    # Setup
    network = Network.from_file(NET_DIR / "small.txt")
    
    # Assertions
    assert network.start == "lozere"
    assert network.end == "saclay"
    assert network._roads == {
        'lozere': [('ensae', 10, 2), ('guichet', 20, 0)], 
        'ensae': [('saclay', 45, 0)], 
        'guichet': [('ensae', 15, 1)],
        'saclay': []
    }

    from network import Network

def test_extended_graph_shortest_path():
    routes_test = {
        'A': [('B', 10, 1), ('C', 20, 0)],
        'B': [('C', 5, 2)],
        'C': []
    }
    
    mon_reseau = Network(roads=routes_test, start='A', end='C')
    graphe_etendu = mon_reseau.build_extended_graph()
    
    distances = graphe_etendu.shortest_path3(depart=('A', 0))
    
    assert distances[('C', 0)] == 20
    assert distances[('C', 3)] == 15
    assert distances[('B', 1)] == 10

def test_shortest_path_small():
    network = Network.from_file(NET_DIR / "small.txt")
    graphe_etendu = network.build_extended_graph()
    distances = graphe_etendu.shortest_path3(depart=(network.start, 0))
    distances_arrivee = [
        dist for (noeud, fatigue), dist in distances.items() 
        if noeud == network.end
    ]
    distance_minimale = min(distances_arrivee)
    assert distance_minimale == 55