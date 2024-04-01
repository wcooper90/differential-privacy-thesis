"""
Script to analyze the accuracy of naive vs. flow-based graph-dp edge count
algorithms, print results.
"""
import math
import time
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm
from datetime import datetime
from node_dp_helpers import exact_count, build_flow_graph, assert_alpha_decay
from dp_edge_count import graph_dp_edge_count, naive_dp_edge_count


# load random graph object from file
G = pickle.load(open('./random-scale-free-graphs/n10000-alpha0.2-beta0.2-gamma0.6.pickle', 'rb'))
# print the number of nodes in the graph
print("True number of nodes in graph G: " + str(G.number_of_nodes()))
# print the maximum degree of the graph
max_degree = sorted(G.degree, key=lambda x: x[1], reverse=True)[0][1]
print("Maximum degree of graph G: " + str(max_degree))
# print the average degree of the graph
node_degrees = [tup[1] for tup in sorted(G.degree, key=lambda x: x[1], reverse=True)]
avg_degree = sum(node_degrees) / len(node_degrees)
print("Average degree: " + str(avg_degree))

n = G.number_of_nodes()
# alpha-decay value, must be greater than 1
alpha = 1.3
print("Alpha decay for alpha = " + str(alpha) + " is satisfied? ")
print(assert_alpha_decay(G, alpha))
# new bounded degree
# create a list of possible bounded degrees D, ignore the first entry because it's too close tp the avg degree
D_options = np.linspace(avg_degree, max_degree, 8)[1:]
# use the bound they set in the paper for their proof, D = n ** (1 / alpha)
# D_options = [n ** (1 / alpha)]

# helper function to generate random seed
def seed_generator():
    return int(float(str(datetime.now().timestamp() * 1000)[5:]))

flow_based_dp_error = {k: [] for k in D_options}
naive_based_dp_error = []
true_num_edges = G.number_of_edges()

# generate 100 random graph instances for each algorithm
for i in tqdm(range(100)):
    for D in D_options:
        seed = seed_generator()
        np.random.seed(seed)
        dp_num_edges = graph_dp_edge_count(G, D, epsilon=1)
        flow_based_dp_error[D].append(dp_num_edges - true_num_edges)

    seed = seed_generator()
    np.random.seed(seed)
    naive_num_edges = naive_dp_edge_count(G, epsilon=1)
    naive_based_dp_error.append(naive_num_edges - true_num_edges)

# calculate errors and error ranges
flow_based_dp_error_intervals = {k: None for k in D_options}
for key in flow_based_dp_error.keys():
    positive_errors = [np.abs(error) for error in flow_based_dp_error[key]]
    p5, p95 = np.percentile(positive_errors, 5), np.percentile(positive_errors, 95)
    flow_based_avg_error = sum(positive_errors) / len(positive_errors)
    flow_based_dp_error_intervals[key] = (p5, p95)
    print("Average error in flow-based graph dp edge count with bound {D}: {avg_error}".format(D=int(key), avg_error=flow_based_avg_error))
    print("90% of data falls into interval: (" + str(p5) + ", " + str(p95) + ")")


# print results
print("*"*80)
positive_naive_errors = [np.abs(error) for error in naive_based_dp_error]
p5, p95 = np.percentile(positive_naive_errors, 5), np.percentile(positive_naive_errors, 95)
naive_dp_error_interval = (p5, p95)
naive_avg_error = sum(positive_naive_errors) / len(positive_naive_errors)
print("Average error in naive graph dp edge count: {naive_avg_error}".format(naive_avg_error=naive_avg_error))
print("90% of data falls into interval: (" + str(p5) + ", " + str(p95) + ")")
