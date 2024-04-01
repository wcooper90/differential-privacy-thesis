"""
Implementation of the node-dp degree distribution algorithm from
Kasiviswanathan et al., "Analyzing Graphs with Node Differential Privacy".
"""
import numpy as np
import pandas as pd
import networkx as nx
import time
import pickle
from node_dp_helpers import *
import random
import matplotlib.pyplot as plt

# load graph object from file
G = pickle.load(open('./random-scale-free-graphs/n1000-alpha0.2-beta0.2-gamma0.6.pickle', 'rb'))

print("Maximum degree of graph G: ")
print(sorted(G.degree, key=lambda x: x[1], reverse=True)[0][1])
node_degrees = [bruh[1] for bruh in sorted(G.degree, key=lambda x: x[1], reverse=True)]
avg_degree = sum(node_degrees) / len(node_degrees)
print("Average degree: " + str(avg_degree))
print("True number of edges in graph G: ")
print(G.number_of_edges())
print("True number of nodes in graph G: ")
print(G.number_of_nodes())

n = G.number_of_nodes()
# alpha-decay value, must be greater than 1
alpha = 1.2
print("Alpha decay for alpha = " + str(alpha) + " is satisfied? ")
print(assert_alpha_decay(G, alpha))

# new bounded degree
# bounded degree D must be an integer
# D = int(n ** (1 / alpha))
D = 30
print("New bounded degree: " + str(D))
epsilon = 1

# naive truncation projection, output graph has maximum degree of D_hat
def naive_truncation(G, D_hat):
    removed_nodes = [node for node, degree in dict(G.degree()).items() if degree > D_hat]
    G.remove_nodes_from(removed_nodes)
    return G


# calculate beta upper smooth bound on the local sensitivity of the naive truncation operator
def naive_truncation_smooth_bound(G, D_hat, epsilon):
    n = G.number_of_nodes()
    beta = epsilon / (2 ** 0.5 * (D_hat + 1))
    degree_upper_bound = D_hat + np.log(n) / beta
    degree_lower_bound = D_hat - np.log(n) / beta
    ell = cumulative_p_g(G, degree_upper_bound) - cumulative_p_g(G, degree_lower_bound)
    S_T_naive = ell + 1 / beta + 1
    return S_T_naive


# calculate a secure degree distribution on input graph G
def graph_dp_degree_distribution(G, D, beta=1, epsilon=0.5):
    n = G.number_of_nodes()
    possible_degree_thresholds = [D + np.log(n) / beta + i for i in range(1, D + 1)]
    D_hat = np.random.choice(possible_degree_thresholds)
    print("Random D_hat: " + str(D_hat))
    naively_truncated_G = naive_truncation(G, D_hat)
    print("Number of nodes in truncated G: " + str(naively_truncated_G.number_of_nodes()))
    print("Number of edges in truncated G: " + str(naively_truncated_G.number_of_edges()))
    S_T_naive = naive_truncation_smooth_bound(G, D_hat, epsilon)
    print("Smooth upper bound on naive truncation: " + str(S_T_naive))
    cauchy_scale = 2 * (2 ** 0.5) * D_hat / epsilon * S_T_naive
    print("Cauchy scale: " + str(cauchy_scale))
    truncated_graph_degree_distribution = [p_g(naively_truncated_G, i) for i in range(n)]
    print(truncated_graph_degree_distribution[:50])
    private_truncated_graph_degree_distribution = [entry + (np.random.standard_cauchy(1)[0] * cauchy_scale) for entry in truncated_graph_degree_distribution]
    return D_hat, private_truncated_graph_degree_distribution


# dp and non-dp degree distribution
D_hat, dp_degree_distribution = graph_dp_degree_distribution(G, D, epsilon=epsilon)
true_degree_distribution = [p_g(G, i) for i in range(n)]

# assertions about input graph structure before results
assert(D_hat > avg_degree)
assert(D_hat > 4 / epsilon * np.log(n))
assert(alpha > 1)

# print results
l1_error = 0
for i in range(len(dp_degree_distribution)):
    l1_error += np.abs(dp_degree_distribution[i] - true_degree_distribution[i])
print("l1_error of differentially private degree distribution: {l1_error}".format(l1_error=l1_error))
paper_error_bound = (avg_degree ** alpha) / (D_hat ** (alpha - 2)) + D_hat ** 3 / n
print("Error bound for algorithm on this graph according to the paper: {error_bound}".format(error_bound=paper_error_bound))

# plot resulting dp and non-dp degree distributions 
x = np.arange(50)
plt.plot(x, dp_degree_distribution[:50])  # Plot the chart
plt.savefig('./dp.png', dpi=300, bbox_inches="tight")
plt.clf()
plt.plot(x, true_degree_distribution[:50])  # Plot the chart
plt.savefig('./true.png', dpi=300, bbox_inches="tight")
