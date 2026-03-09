from network import Network

path = "/home/onyxia/work/Ensae-Prog-26/examples/"
tests = [("small.txt", 125), ("medium-nofatigue.txt", 1771), ("medium-smallfatigue.txt", 29934), (
    "medium-largefatigue.txt", 3462368), ("large-nofatigue.txt", 15137), 
    ("large-smallfatigue.txt", 2000993), ("large-largefatigue.txt", 288955255)]

for fichier, attendu in tests:
    network = Network.from_file(path + fichier)
    g_implicite = network.build_implicit_graph()
    resultat = g_implicite.shortest_path((network.start, 0), network.end)
    print(f"{fichier} : {resultat}")