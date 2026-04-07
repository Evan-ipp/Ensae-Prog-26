import time
from network import Network
from graph import creer_heuristique

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

print("============================================================")
print(" TEST 1 : Graphe Etendu (Dijkstra Classique)")
print(" Limite aux 3 premiers fichiers pour eviter le MemoryError")
print("============================================================")

for fichier, attendu in tests[:3]:
    network = Network.from_file(path + fichier)
    
    start_time = time.time()
    g_extended = network.build_extended_graph()
    resultat = g_extended.shortest_path((network.start, 0), network.end)
    end_time = time.time()
    
    duree = end_time - start_time
    print(f"{fichier:25} | Resultat: {resultat} (Attendu: {attendu}) | Temps: {duree:.4f} sec")


print("\n============================================================")
print(" TEST 2 : Graphe Implicite (Comparaison Dijkstra vs A*)")
print("============================================================")

for fichier, attendu in tests:
    network = Network.from_file(path + fichier)
    g_implicite = network.build_implicit_graph()
    
    # --- 1. Resolution sans heuristique (Dijkstra classique) ---
    start_time_dijkstra = time.time()
    res_dijkstra = g_implicite.shortest_path((network.start, 0), network.end)
    end_time_dijkstra = time.time()
    duree_dijkstra = end_time_dijkstra - start_time_dijkstra
    
    # --- 2. Resolution avec heuristique (Algorithme A*) ---
    start_time_astar = time.time()
    # On inclut le temps de creation de l'heuristique dans le chrono de A*
    h = creer_heuristique(network, network.end)
    res_astar = g_implicite.shortest_path((network.start, 0), network.end, heuristique=h)
    end_time_astar = time.time()
    duree_astar = end_time_astar - start_time_astar
    
    # --- 3. Calcul et affichage des performances ---
    gain_absolu = duree_dijkstra - duree_astar
    gain_relatif = (gain_absolu / duree_dijkstra * 100) if duree_dijkstra > 0 else 0

    print(f"\n[Fichier] {fichier} (Attendu: {attendu})")
    print(f"  - Dijkstra : {res_dijkstra} calcule en {duree_dijkstra:.4f} sec")
    print(f"  - A* : {res_astar} calcule en {duree_astar:.4f} sec")
    
    if gain_absolu > 0:
        print(f"  > Bilan    : Gain de {gain_absolu:.4f} sec ({gain_relatif:.1f}% plus rapide)")
    else:
        print(f"  > Bilan    : Perte de {-gain_absolu:.4f} sec (Surcout lie au calcul de l'heuristique)")
        
    if res_dijkstra != attendu or res_astar != attendu:
        print("  [ERREUR] Le resultat obtenu differe du resultat attendu.")

print("\nFin de l'execution des tests.")