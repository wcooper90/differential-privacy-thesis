"""
Script to use graph-dp edge count algorithm from Kasiviswanathan et al.,
"Analyzing Graphs with Node Differential Privacy". Prints results on subgraphs
of connections across distinct time spans.
"""
import pickle
import numpy as np
import pandas as pd
import networkx as nx

from alpha_decay import assert_alpha_decay
from dp_edge_count import naive_dp_edge_count, graph_dp_edge_count

# reconfigure system path to import OpenDP measurements and transformations
import sys
sys.path.append('../')
from transformations import *
# time bins defined by the construction of graph objects in ./construct_graph.py
time_bins = ['2000_to_2004', '2004_to_2008', '2008_to_2012', '2012_to_2016', '2016_to_2020', '2020_to_2024']
# load in the graphs
graphs = []
for time_bin in time_bins:
    graphs.append(pickle.load(open('./constructed-graphs/' + time_bin + '.pickle', 'rb')))

flow_based_edge_counts = []
naive_edge_counts = []
dp_node_counts = []

# alpha-decay value, must be greater than 1
alpha = 1.5
for G in graphs:
    print("*"*80)
    # print the number of nodes in the graph
    n = G.number_of_nodes()
    e = G.number_of_edges()
    # print the maximum degree of the graph
    max_degree = sorted(G.degree, key=lambda x: x[1], reverse=True)[0][1]
    # print the average degree of the graph
    node_degrees = [bruh[1] for bruh in sorted(G.degree, key=lambda x: x[1], reverse=True)]
    avg_degree = sum(node_degrees) / len(node_degrees)

    # assert alpha decay holds
    print("Alpha decay for alpha = " + str(alpha) + " is satisfied? ")
    if assert_alpha_decay(G, alpha):
        print("Yes. ")
    else:
        print("No. Breaking... ")
        break

    # set bound to be D = n ** (1/alpha) for flow based mechanism
    D = n ** (1 / alpha)
    # calculate graph dp release for number of edges
    naive_dp_edges = naive_dp_edge_count(G, epsilon=1)
    flow_based_dp_edges = graph_dp_edge_count(G, D, epsilon=1)

    # store results
    print("Naive graph dp count of edges: {naive_dp_edges}".format(naive_dp_edges=naive_dp_edges))
    print("Flow-based graph dp count of edges: {flow_based_dp_edges}".format(flow_based_dp_edges=flow_based_dp_edges))
    naive_edge_counts.append(naive_dp_edges)
    flow_based_edge_counts.append(flow_based_dp_edges)

    # use OpenDP methods to make a private release of number of nodes in the graph
    # by first converting the graph back to a dataframe
    df_values = np.zeros(n)
    df = pd.DataFrame(df_values)
    # rename the only column to 'index'
    df = df.rename(columns={0: "index"})
    # each node only contributes one row
    max_contributions = 1
    # define metadata according to df structure
    metadata = {"column_names": ["index"]}
    # create column transformation
    col_trans = create_col_trans("index", str, metadata)
    # create the counting transformation
    count_trans = create_count_trans(col_trans)
    # create the counting measurement
    count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)
    # make the private count release
    dp_node_count = count_meas(df.to_csv())

    # store results
    dp_node_counts.append(dp_node_count)


# print dp results 
print("Final naive edge counts: ")
print(naive_edge_counts)
print("Final flow-based edge counts: ")
print(flow_based_edge_counts)
print("DP node counts: ")
print(dp_node_counts)
naive_avg_connections = [2 * naive_edge_counts[i] / dp_node_counts[i] for i in range(len(naive_edge_counts))]
flow_based_avg_connections = [2 * flow_based_edge_counts[i] / dp_node_counts[i] for i in range(len(flow_based_edge_counts))]
print("*"*80)
print("Naive average connections over time: ")
print(naive_avg_connections)
print("Flow-based average connections over time: ")
print(flow_based_avg_connections)
