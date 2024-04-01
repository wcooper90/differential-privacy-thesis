"""
Script to generate and store random scale free graphs
"""
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime
import pickle
import time
fig = plt.figure(figsize=(12,12))
ax = plt.subplot(111)
ax.set_title('Graph - Shapes', fontsize=10)

# scale free graph parameters
# number of nodes in the graph
n = 1000000
# from https://networkx.org/documentation/stable/reference/generated/networkx.generators.directed.scale_free_graph.html
# Probability for adding a new node connected to an existing node chosen randomly according to the in-degree distribution.
alpha = 0.2
# Probability for adding an edge between two existing nodes. One existing node is chosen randomly according the in-degree distribution and the other chosen randomly according to the out-degree distribution.
beta = 0.2
# Probability for adding a new node connected to an existing node chosen randomly according to the out-degree distribution.
gamma = 0.6

# create graph
G = nx.scale_free_graph(n, alpha=alpha, beta=beta, gamma=gamma, delta_in=0, delta_out=0)
# make the graph undirected
G = G.to_undirected()

# layout for plotting, only plot if fewer than 5001 nodes
if n <= 5000:
    file_name = "./random-scale-free-graph-plots/{n}nodes.png".format(n=n)
    pos = nx.spring_layout(G)
    nx.draw(G, pos, node_size=100, node_color='blue', font_size=8, font_weight='bold')
    plt.tight_layout()
    plt.savefig(file_name, format="PNG")


print("Number of nodes in G: " + str(n))
print("Maximum degree of graph G: ")
print(sorted(G.degree, key=lambda x: x[1], reverse=True)[0][1])
print("Number of disjoint components: " + str(nx.number_connected_components(G)))
print("Number of edges: " + str(G.number_of_edges()))
print("Average node degree: " + str(G.number_of_edges() / G.number_of_nodes()))

# function to save the graph 
def save_graph(G, file_name=None):
    try:
        if file_name is None:
            file_name = str(datetime.now())[:10]
        s = time.time()
        pickle.dump(G, open('./random-scale-free-graphs/' + file_name + '.pickle', 'wb'))
        e = time.time()
        t = round(e - s, 4)
        print("Successfully saved graph to ./random-scale-free-graphs/" + file_name + ".pickle, took " + str(t) + " seconds.")
    except Exception as e:
        print("Could not save graph to pickle file! See exception below... ")
        print(e)

file_name = "n{n}-alpha{alpha}-beta{beta}-gamma{gamma}".format(n=n, alpha=alpha, beta=beta, gamma=gamma)
save_graph(G, file_name)
