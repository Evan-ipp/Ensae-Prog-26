import time
import random
from network import Network
from graph import creer_heuristiques

if __name__ == "__main__":
    path = "/home/onyxia/work/Ensae-Prog-26/examples/"

    tests = [
        ("small.txt", 125), 
        ("medium-nofatigue.txt", 1771), 
        ("medium-smallfatigue.txt", 29934), 
        ("medium-largefatigue.txt", 3462368), 
        ("large-nofatigue.txt", 15137), 
        ("large-smallfatigue.txt", 2000993), 
        ("large-largefatigue.txt", 288955255)
    ]

    fichiers_a_ignorer_pour_dijkstra = ["large-largefatigue.txt"]

    print("\nGraphe Etendu (Dijkstra Classique)")
    for fichier, attendu in tests[:3]:
        network = Network.from_file(path + fichier)
        start_time = time.time()
        g_extended = network.build_extended_graph()
        resultat = g_extended.shortest_path((network.start, 0), network.end)
        duree = time.time() - start_time
        print(f"{fichier:25}, Cout: {resultat}, Temps: {duree:.4f} s")

    print("\nGraphe Implicite (Dijkstra vs A* H1 vs A* H2)")
    for fichier, attendu in tests:
        network = Network.from_file(path + fichier)
        g_implicite = network.build_implicit_graph()
        
        if fichier in fichiers_a_ignorer_pour_dijkstra:
            res_dijkstra, duree_dijkstra = "Ignore", 0.0
        else:
            start_time = time.time()
            res_dijkstra = g_implicite.shortest_path((network.start, 0), network.end)
            duree_dijkstra = time.time() - start_time
        
        h_simple, h_fatigue = creer_heuristiques(network, network.end)
        
        start_time = time.time()
        res_h1 = g_implicite.shortest_path((network.start, 0), network.end, heuristique=h_simple)
        duree_h1 = time.time() - start_time
        
        start_time = time.time()
        res_h2 = g_implicite.shortest_path((network.start, 0), network.end, heuristique=h_fatigue)
        duree_h2 = time.time() - start_time
        
        print(f"\n{fichier} (Attendu: {attendu})")
        if res_dijkstra != "Ignore":
            print(f"  Dijkstra       : {res_dijkstra} ({duree_dijkstra:.4f} s)")
        else:
            print(f"  Dijkstra       : Non execute")
        print(f"  A* (H1 Simple) : {res_h1} ({duree_h1:.4f} s)")
        print(f"  A* (H2 Fatigue): {res_h2} ({duree_h2:.4f} s)")

    print("\nExtension 1 : Missions Multiples (Explosion Combinatoire)")
    
    fichier_test = "medium-nofatigue.txt"
    reseau = Network.from_file(path + fichier_test)
    villes = list(reseau._roads.keys())
    
    random.seed(42) 

    for k in [2, 4, 10]:
        print(f"\nTest avec {k} missions sur {fichier_test}")
        
        missions = [tuple(random.sample(villes, 2)) for _ in range(k)]
        
        # 1. Ordre Impose
        g_multi_ordonne, cibles = reseau.construire_graphe_missions_ordonnees(missions)
        start_node = missions[0][0]
        etape_depart = 0
        while etape_depart < len(cibles) and start_node == cibles[etape_depart]:
            etape_depart += 1
            
        start_t = time.time()
        cout_ordonne = g_multi_ordonne.shortest_path(((start_node, etape_depart), 0), (cibles[-1], len(cibles)))
        duree_ordonne = time.time() - start_t
        print(f"  Ordre Impose : Cout = {cout_ordonne}, Temps = {duree_ordonne:.4f} s")
        
        # 2. Ordre Libre
        g_multi_libre = reseau.construire_graphe_missions_libres(missions)
        start_t = time.time()
        
        # Utilisation de l'etat final corrige : ("ZZZ_FIN", frozenset(), -1)
        cout_libre = g_multi_libre.shortest_path(((start_node, frozenset(), -1), 0), ("ZZZ_FIN", frozenset(), -1))
        
        duree_libre = time.time() - start_t
        print(f"  Ordre Libre  : Cout = {cout_libre}, Temps = {duree_libre:.4f} s")

    print("\nFin de l'execution.")