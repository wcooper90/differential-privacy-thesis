"""
Node differential privacy helper functions: exact graph degree calculations,
alpha-decay assertion, flow-graph construction, bounded-degree-quasiflow function
"""
# help from https://github.com/anusii/graph-dp/blob/master/node_differential_privacy.ipynb
import numpy as np
import networkx as nx
import scipy.optimize
import scipy.interpolate
import scipy.special
import time
import logging
import pickle
from tqdm import tqdm

# from https://www.geeksforgeeks.org/logging-in-python/
# Create and configure logger
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# graph degree functions
# exact degree distribution
def p_g(degree_sequence, k):
    return len([i for i in degree_sequence if i==k]) / len(degree_sequence)
# cumulative degree distribution
def P_g(degree_sequence, k):
    return len([i for i in degree_sequence if i >= k]) / len(degree_sequence)
# average degree
def avg_degree(num_edges, num_nodes):
    return 2 * num_edges / num_nodes


# compute an exact count based on graph query function h
def exact_count(G, h, verbose=False):
    """
    Compute the exact value of a query which is linear in the degree distribution of G

    Parameters:
        G: An undirected graph
        h: An array describing a query which is linear in the degree distribution of G

    Returns:
        The exact value of the query evaluated on G.
    """
    if verbose:
        logging.info("----------BEGINNING EXACT_COUNT OPERATION----------")

    s = time.time()
    x = np.arange(len(h))
    h_fun = scipy.interpolate.interp1d(x, h)
    e = time.time()
    t = str(round(e - s, 4))
    if verbose:
        logging.info("scipy interpolation completed in {ftime_elapsed} seconds".format(ftime_elapsed=t))

    s = time.time()
    degree_histogram = np.array(nx.degree_histogram(G))
    e = time.time()
    t = str(round(e - s, 4))
    if verbose:
        logging.info("degree histogram built in {ftime_elapsed} seconds".format(ftime_elapsed=t))


    s = time.time()
    exact_count = degree_histogram @ h_fun(np.arange(len(degree_histogram)))
    e = time.time()
    t = str(round(e - s, 4))
    if verbose:
        logging.info("exact_count operation performed successfully in {ftime_elapsed} seconds".format(ftime_elapsed=t))
    return exact_count


# build a flow graph of G with a specified bound D
def build_flow_graph(G, D, verbose=False):
    """
    Build a flow graph for G

    Parameters:
        G: An undirected graph
        D: The capacity for edges between nodes of G and
           the source/sink nodes in the flow graph

    Returns:
        A flow graph whose max flow yields an approximate query response
    """
    if verbose:
        logging.info("----------BEGINNING BUILD_FLOW_GRAPH OPERATION----------")

    s = time.time()
    V_left = list(zip(["left"] * len(G), G.nodes()))
    V_right = list(zip(["right"] * len(G), G.nodes()))
    F = nx.DiGraph()
    F.add_nodes_from(V_left)
    F.add_nodes_from(V_right)
    F.add_nodes_from("st")
    F.add_weighted_edges_from([("s", vl, D) for vl in V_left], weight="capacity")
    F.add_weighted_edges_from([(vr, "t", D) for vr in V_right], weight="capacity")
    F.add_weighted_edges_from(
        [(("left", u), ("right", v), 1) for u, v in G.edges()], weight="capacity"
    )
    F.add_weighted_edges_from(
        [(("left", v), ("right", u), 1) for u, v in G.edges()], weight="capacity"
    )
    e = time.time()
    t = str(round(e - s, 4))

    if verbose:
        logging.info("build_flow_graph operation performed successfully in {ftime_elapsed} seconds".format(ftime_elapsed=t))

    return F


# Generalized dp-count algorithm on D-bounded graphs from
# Kasiviswanathan et al., "Analyzing Graphs with Node Differential Privacy"
# code from https://github.com/anusii/graph-dp/blob/master/node_differential_privacy.ipynb
def bounded_degree_quasiflow(F, h, D, verbose=False):
    """
    Parameters:
        F: An undirected graph
        h: An array describing a query which is linear in the degree distribution of G
        D: A bound on the capacities in the flow graph derived from G

    Returns:
        The maximal value for \max_{f \in flows} \sum{v \in F} h(f(v))
    """
    if verbose:
        logging.info("----------BEGINNING BOUNDED_DEGREE_QUASIFLOW OPERATION----------")

    s = time.time()
    nodes = list(F.nodes())
    edges = list(F.edges())
    adjacency = np.zeros((len(nodes), len(edges)))
    for j in range(len(edges)):
        i0 = nodes.index(edges[j][0])
        i1 = nodes.index(edges[j][1])
        adjacency[i0, j] = -1
        adjacency[i1, j] = 1
    e = time.time()
    t = str(round(e - s, 4))
    if verbose:
        logging.info("adjacency matrix finished building in {ftime_elapsed} seconds".format(ftime_elapsed=t))

    # setting up minimization problem
    capacities = np.array([F.edges[e]["capacity"] for e in F.edges()])
    x0 = np.random.random(capacities.size) * capacities
    mask = np.array([("s" in edge) for edge in edges])
    bounds = [(0, capacity) for capacity in capacities]
    constraint = scipy.optimize.LinearConstraint(adjacency[:-2], 0, 0)

    s = time.time()
    x = np.arange(D + 1)
    h_fun = scipy.interpolate.interp1d(x, h[:D+1])
    f = lambda x, *args: -np.sum(h_fun(x[tuple(args[0])]))
    res = scipy.optimize.minimize(
        fun=f, x0=x0, args=[mask], bounds=bounds, constraints=[constraint], options={'disp': True}
    )
    e = time.time()
    t = str(round(e - s, 4))
    if verbose:
        logging.info("bounded_degree_quasiflow operation performed successfully in {ftime_elapsed} seconds".format(ftime_elapsed=t))
    return -res.fun


# check to see if an input graph satisfies alpha decay for a given alpha
def assert_alpha_decay(G, alpha):
    assert(alpha > 1)
    num_nodes = G.number_of_nodes()
    num_edges = G.number_of_edges()
    degree_sequence = [tup[1] for tup in sorted(G.degree, key=lambda x: x[1], reverse=True)]
    avg_d = avg_degree(num_edges, num_nodes)

    # t needs to be larger than 1 and a sufficiently large natural number.
    # num_nodes is appropriate here because we know in the HCS dataset the
    # average degree is at least 1
    max_t = num_nodes
    for t in tqdm(range(1, max_t + 1)):
        int_cumulative_degree_distribution = P_g(degree_sequence, t * avg_d)
        if int_cumulative_degree_distribution > t ** (-alpha):
            print("*"*80)
            print("Did not satisfy old alpha decay!")
            return False
        # is this correct?
        float_cumulative_degree_distribution = P_g(degree_sequence, (t + 0.001) * avg_d)
        if float_cumulative_degree_distribution > (t + 0.001) ** (-alpha):
            print("*"*80)
            print("Did not satisfy new alpha decay!")
            return False

        # can terminate this loop early if t * avg_d is more than the number of nodes
        # because P_g will always evaluate to 0 after this, and cannot be greater than t ** (-alpha)
        if t * avg_d > max_t:
            break
    return True
