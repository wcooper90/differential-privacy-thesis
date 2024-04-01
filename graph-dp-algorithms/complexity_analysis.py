"""
Script to run three graph-dp algorithms on random binomial graphs of varying sizes,
measures compute time and writes to disk
"""
# help from https://github.com/anusii/graph-dp/blob/master/node_differential_privacy.ipynb
import numpy as np
import pandas as pd
import networkx as nx
import time
import pickle
import scipy.optimize
import scipy.interpolate
import scipy.special
from node_dp_helpers import exact_count, build_flow_graph, bounded_degree_quasiflow
from dp_edge_count import graph_dp_edge_count

# global static constants
DEFAULT_NODE_SCALE = 3
k = 3
D_BOUNDS = [2, 4, 6, 8, 12, 16, 20]
epsilon = 1.0

# lists to keep track of runtimes
max_flow_edge_count_times = []
opt_based_edge_count_times = []
opt_based_kstar_count_times = []

for i in range(7):
    # number of nodes in the graph
    n = 2 ** (DEFAULT_NODE_SCALE + i)
    # probability of a connection between two nodes
    p = 2 ** -(DEFAULT_NODE_SCALE + i - 1)
    # generate binomial graph
    G = nx.random_graphs.gnp_random_graph(n, p)

    # define edge count query
    h_edge = np.arange(n + 1) / 2.0
    # find exact edge count
    edge_count = exact_count(G, h_edge)

    # define k-star count query
    h_kstar = scipy.special.comb(np.arange(n + 1), k)
    # find exact k-start count
    kstar_count = exact_count(G, h_kstar)

    # define bound for bounded degree graph
    D = D_BOUNDS[i]

    print("Graph with {n} nodes, probability {p} of an edge, D bound of {D}".format(n=n, p=p, D=D))
    print("Exact edge count = %f" % edge_count)
    print("Exact %i-star count = %f" % (k, kstar_count))

    # build flow graph
    buildling_flow_graph_start_time = time.time()
    F = build_flow_graph(G, D)
    buildling_flow_graph_end_time = time.time()
    # factor in this time to optimization-based edge count and kstar count
    time_to_build_flow_graph = buildling_flow_graph_end_time - buildling_flow_graph_start_time

    # optimization-based edge count
    opt_edge_count_start_time = time.time()
    bd_quasiflow_edge = bounded_degree_quasiflow(F, h_edge, D)
    opt_edge_count_end_time = time.time()
    time_to_count_opt_edge = round(opt_edge_count_end_time - opt_edge_count_start_time + time_to_build_flow_graph, 5)
    # optimization-based kstar count
    opt_kstar_count_start_time = time.time()
    bd_quasiflow_kstar = bounded_degree_quasiflow(F, h_kstar, D)
    opt_kstar_count_end_time = time.time()
    time_to_count_opt_kstar = round(opt_kstar_count_end_time - opt_kstar_count_start_time + time_to_build_flow_graph, 5)
    # max-flow-based edge count
    max_flow_edge_count_start = time.time()
    max_flow_edge_count = graph_dp_edge_count(G, D, epsilon=epsilon)
    max_flow_edge_count_end = time.time()
    time_to_count_max_flow_edge = round(max_flow_edge_count_end - max_flow_edge_count_start, 5)

    # add noise to optimization-based edge count
    sensitivity_edge = np.max(h_edge[:(D+1)]) + np.max(h_edge[1:(D+1)] - h_edge[:D])
    edge_laplacian_noise = np.random.laplace(0., sensitivity_edge / epsilon)
    dp_opt_edge_count = bd_quasiflow_edge + edge_laplacian_noise

    # add noise to optimization-based kstar count
    # Note: The sensitivity of the kstar count is much greater than that of the edge and node counts
    # error is much higher, especially on smaller graphs
    sensitivity_kstar = np.max(h_kstar[:(D+1)]) + np.max(h_kstar[1:(D+1)] - h_kstar[:D])
    kstar_laplacian_noise = np.random.laplace(0., sensitivity_kstar / epsilon)
    dp_kstar_count = bd_quasiflow_kstar + kstar_laplacian_noise

    # Edge count
    print("Approximate edge count = %f" % bd_quasiflow_edge)
    print("Optimization private edge count = %f\n" % dp_opt_edge_count)
    print("Max-flow private edge count = %f\n" % max_flow_edge_count)

    # kstar count
    print("Approximate %i-star count = %f" % (k, bd_quasiflow_kstar))
    print("Differentially private %i-star count = %f\n" % (k, dp_kstar_count))

    print("Time to calculate DP Opimization edge count: {t}".format(t=time_to_count_opt_edge))
    print("Time to calculate DP Opimization kstar count: {t}".format(t=time_to_count_opt_kstar))
    print("Time to calculate DP Max-flow edge count: {t}".format(t=time_to_count_max_flow_edge))
    print("*"*80)

    # keep track of timing globally
    max_flow_edge_count_times.append(time_to_count_max_flow_edge)
    opt_based_edge_count_times.append(time_to_count_opt_edge)
    opt_based_kstar_count_times.append(time_to_count_opt_kstar)


# store the dictionary for a bar chart with runtimes
dp_graph_algo_runtimes = {"max-flow-edge-count": max_flow_edge_count_times,
                            "opt-based-edge-count": opt_based_edge_count_times,
                            "opt-based-kstar-count": opt_based_kstar_count_times}

# write to disk
f = open("./dp_graph_algo_runtimes.txt", "w")
f.write(json.dumps(dp_graph_algo_runtimes))
f.close()
