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

print("\nFin de l'execution des tests de base.")


# ============================================================
#  TEST EXTENSION 1 : Missions Multiples Ordonnees
# ============================================================
print("\n============================================================")
print(" TEST EXTENSION 1 : Missions Multiples Ordonnees")
print("============================================================")

fichier_ext1 = "small.txt"
network_ext1 = Network.from_file(path + fichier_ext1)

# Definition des missions : l'agent doit faire 0->2, puis 1->4
missions = [("0", "2"), ("1", "4")]

g_multi, cibles = network_ext1.build_multimission_implicit_graph(missions)

start_node = missions[0][0]
etape_depart = 0

# Ajustement au cas ou le point de depart valide deja une cible
while etape_depart < len(cibles) and start_node == cibles[etape_depart]:
    etape_depart += 1

etat_initial = ((start_node, etape_depart), 0)
etat_final_attendu = (cibles[-1], len(cibles))

start_time_ext1 = time.time()
cout_minimal_ordonne = g_multi.shortest_path(etat_initial, etat_final_attendu)
duree_ext1 = time.time() - start_time_ext1

print(f"[Fichier] {fichier_ext1}")
print(f"  - Missions imposees : {missions}")
print(f"  - Cibles successives a valider : {cibles}")
print(f"  - Cout total optimal trouve : {cout_minimal_ordonne}")
print(f"  - Temps de calcul : {duree_ext1:.4f} sec")


# ============================================================
#  TEST EXTENSION 1 (Variante) : Missions Multiples Ordre Libre
# ============================================================
print("\n============================================================")
print(" TEST EXTENSION 1 (Variante) : Missions Multiples Ordre Libre")
print("============================================================")

fichier_ext1_libre = "small.txt"
network_ext1_libre = Network.from_file(path + fichier_ext1_libre)

missions_libres = [("0", "2"), ("1", "4")]

g_multi_libre = network_ext1_libre.build_free_order_multimission_graph(missions_libres)

# L'etat initial : on demarre de "0", on n'a accompli aucune mission (frozenset vide), et on est libre (-1)
etat_initial_libre = ((network_ext1_libre.start, frozenset(), -1), 0)

start_time_libre = time.time()
cout_minimal_libre = g_multi_libre.shortest_path(etat_initial_libre, "ETAT_FINAL")
duree_libre = time.time() - start_time_libre

print(f"[Fichier] {fichier_ext1_libre}")
print(f"  - Missions disponibles : {missions_libres}")
print(f"  - Cout minimal optimal (ordre libre) : {cout_minimal_libre}")
print(f"  - Temps de calcul : {duree_libre:.4f} sec")