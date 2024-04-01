"""
Implementation of the node-dp max-flow based edge count algorithm from
Kasiviswanathan et al., "Analyzing Graphs with Node Differential Privacy".
"""
import numpy as np
import networkx as nx
from node_dp_helpers import build_flow_graph


# naive graph dp edge count, just add Laplace noise scaled to n + 1
def naive_dp_edge_count(G, epsilon=0.5):
    return G.number_of_edges() + np.random.laplace(0, (G.number_of_nodes() + 1) / epsilon)


# flow-based graph dp edge count
def graph_dp_edge_count(G, D, epsilon=0.5, verbose=False):
    # assert that selected bound D is greater than the true average degree of nodes in the graph
    node_degrees = [node[1] for node in sorted(G.degree, key=lambda x: x[1], reverse=True)]
    avg_degree = sum(node_degrees) / len(node_degrees)
    if verbose:
        print("Average degree: {avg_degree}".format(avg_degree=avg_degree))
        print("Bound D: {D}".format(D=D))
    assert(D > avg_degree)

    # define threshold, check e_hat_1
    true_num_edges = G.number_of_edges()
    n = G.number_of_nodes()
    lap_scale = 2 * n / epsilon
    e_hat_1 = true_num_edges + np.random.laplace(0, lap_scale)
    threshold = n * np.log(n) / epsilon
    if e_hat_1 >= 5 * threshold:
        if verbose:
            print("e_hat_1 was greater than the threshold. ")
        return e_hat_1

    # else, build a flow graph and optimize for maximum flow
    F = build_flow_graph(G, D)
    approximate_edge_count, flow_dict = nx.maximum_flow(F, "s", "t")

    if verbose:
        print("e_hat_1 was less than the threshold. ")
        print("Approximate edge count calculated from flow graph: " + str(approximate_edge_count))

    new_scale = 2 * D / epsilon
    e_hat_2 = approximate_edge_count / 2 + np.random.laplace(0, new_scale)
    return e_hat_2
