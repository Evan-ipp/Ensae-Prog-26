import time
from network import Network

path = "/home/onyxia/work/Ensae-Prog-26/examples/"

# La liste complete de tes fichiers
fichiers_a_tester = [
    "small.txt", 
    "medium-nofatigue.txt", 
    "medium-smallfatigue.txt", 
    "medium-largefatigue.txt", 
    "large-nofatigue.txt", 
    "large-smallfatigue.txt", 
    "large-largefatigue.txt"
]

print("\n" + "="*60)
print(" TEST EXTENSION 1 : Ordre Imposé vs Ordre Libre")
print(" Exécution sur l'ensemble des fichiers disponibles")
print("="*60)

for fichier in fichiers_a_tester:
    print(f"\n{'='*50}")
    print(f"---> Analyse du fichier : {fichier}")
    
    # SECURITE : Si on ne veut pas bloquer le PC sur les plus gros fichiers
    if fichier in ["large-smallfatigue.txt", "large-largefatigue.txt"]:
        print("  [Attention] Ce fichier est gigantesque. Le calcul exact va prendre plusieurs minutes.")
        # Decommente la ligne ci-dessous (continue) si tu veux sauter ces fichiers pour aller plus vite
        # continue 

    reseau = Network.from_file(path + fichier)
    
    villes = list(reseau._roads.keys())
    
    if len(villes) < 4:
        print("  [Erreur] Pas assez de villes dans ce fichier pour créer 2 missions.")
        continue
    
    # Generation automatique de 2 missions (soit 2! = 2 ordres possibles à tester en ordre libre)
    missions = [(villes[0], villes[1]), (villes[2], villes[3])]
    
    # Correction manuelle pour small.txt afin d'eviter l'infini si on le souhaite
    if fichier == "small.txt":
        missions = [('lozere', 'guichet'), ('ensae', 'saclay')]
        
    print(f"  Missions testees : {missions}")
    
    # --------------------------------------------------------
    # 1. TEST : ORDRE IMPOSÉ
    # --------------------------------------------------------
    try:
        g_multi_ordonne, cibles = reseau.build_multimission_implicit_graph(missions)
        
        start_node = missions[0][0]
        etape_depart = 0
        while etape_depart < len(cibles) and start_node == cibles[etape_depart]:
            etape_depart += 1
            
        etat_initial_ordonne = ((start_node, etape_depart), 0)
        etat_final_ordonne = (cibles[-1], len(cibles))
        
        start_t = time.time()
        cout_ordonne = g_multi_ordonne.shortest_path(etat_initial_ordonne, etat_final_ordonne)
        duree_ordonne = time.time() - start_t
        
        print(f"  [Ordre Imposé] Cout optimal : {cout_ordonne} (calculé en {duree_ordonne:.4f} sec)")
    except Exception as e:
        print(f"  [Ordre Imposé] Erreur : {e}")
        cout_ordonne = float('inf')
    
    # --------------------------------------------------------
    # 2. TEST : ORDRE LIBRE
    # --------------------------------------------------------
    try:
        g_multi_libre = reseau.build_free_order_multimission_graph(missions)
        
        etat_initial_libre = ((start_node, frozenset(), -1), 0)
        
        start_t = time.time()
        cout_libre = g_multi_libre.shortest_path(etat_initial_libre, "ETAT_FINAL")
        duree_libre = time.time() - start_t
        
        print(f"  [Ordre Libre]  Cout optimal : {cout_libre} (calculé en {duree_libre:.4f} sec)")
    except Exception as e:
        print(f"  [Ordre Libre] Erreur : {e}")
        cout_libre = float('inf')
    
    # --------------------------------------------------------
    # 3. CONCLUSION
    # --------------------------------------------------------
    if cout_libre < cout_ordonne:
        print("  -> Bilan : L'ordre libre a trouvé un chemin globalement PLUS COURT ! 🚀")
    elif cout_libre == cout_ordonne and cout_libre != float('inf'):
        print("  -> Bilan : L'ordre imposé était déjà la meilleure solution possible.")