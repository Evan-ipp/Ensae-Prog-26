import time
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
        print(f"  A* (h1 Simple) : {res_h1} ({duree_h1:.4f} s)")
        print(f"  A* (h2 Fatigue): {res_h2} ({duree_h2:.4f} s)")

<<<<<<< HEAD
    print("\nExtension 1 : Missions Multiples (Ordre Impose vs Libre)")
    fichiers_ext1 = ["small.txt", "medium-nofatigue.txt", "medium-smallfatigue.txt", "large-nofatigue.txt"]

    for fichier in fichiers_ext1:
        reseau = Network.from_file(path + fichier)
        villes = list(reseau._roads.keys())
        
        if len(villes) >= 4:
            missions = [(villes[0], villes[1]), (villes[2], villes[3])]
        if fichier == "small.txt":
            missions = [('lozere', 'guichet'), ('ensae', 'saclay')]
            
        print(f"\n{fichier}, Missions : {missions}")
        
        # 1. Ordre Impose
        g_multi_ordonne, cibles = reseau.construire_graphe_missions_ordonnees(missions)
        start_node = missions[0][0]
        etape_depart = 0
        while etape_depart < len(cibles) and start_node == cibles[etape_depart]:
            etape_depart += 1
            
        start_t = time.time()
        cout_ordonne = g_multi_ordonne.shortest_path(((start_node, etape_depart), 0), (cibles[-1], len(cibles)))
        duree_ordonne = time.time() - start_t
        
        # 2. Ordre Libre
        g_multi_libre = reseau.construire_graphe_missions_libres(missions)
        start_t = time.time()
        cout_libre = g_multi_libre.shortest_path(((start_node, frozenset(), -1), 0), "etat final")
        duree_libre = time.time() - start_t
        
        print(f"  Ordre Impose : Cout = {cout_ordonne}, Temps = {duree_ordonne:.4f} s")
        print(f"  Ordre Libre  : Cout = {cout_libre}, Temps = {duree_libre:.4f} s")

        if cout_libre < cout_ordonne:
            print("  -> L'ordre libre optimise le cout global.")

    print("\nFin de l'execution.")
=======
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
>>>>>>> 78bd5feffe9b1b7911e07cb00d415368b67c4689
