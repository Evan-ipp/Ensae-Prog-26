from network import Network
from graph import Graph

# Load the network
network_file = "/home/onyxia/work/Ensae-Prog-26/examples/small.txt"
network = Network.from_file(network_file)


g = network.build_simple_graph()
print(g._edges)

gpr = {0: [(1, 21), (2, 12)], 1: [(0, 74), (2, 32)], 2 : []}
gp = Graph(gpr)
print(gp.shortest_path())





