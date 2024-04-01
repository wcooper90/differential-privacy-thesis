"""
Script to use graph-dp edge count algorithm from Kasiviswanathan et al.,
"Analyzing Graphs with Node Differential Privacy". Prints results on subgraphs
constructed only from specific domains.
"""
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from node_dp_helpers import assert_alpha_decay
from dp_edge_count import naive_dp_edge_count, graph_dp_edge_count
# reconfigure system path to import OpenDP measurements and transformations
import sys
sys.path.append('../')
from opendp_helpers import *

file_names = ['1999-2025--fas.harvard.edu-fas.harvard.edu', '1999-2025--fas.harvard.edu-college.harvard.edu', '1999-2025--fas.harvard.edu-gmail.com', '1999-2025--college.harvard.edu-college.harvard.edu', '1999-2025--college.harvard.edu-gmail.com', '1999-2025--gmail.com-gmail.com']
# storage structure initialization
fas_fas = []
fas_college = []
fas_gmail = []
college_college = []
college_gmail = []
gmail_gmail = []
for file_name in file_names:
    if "fas.harvard.edu-fas.harvard.edu" in file_name:
        fas_fas.append(file_name)
    elif "fas.harvard.edu-college.harvard.edu" in file_name:
        fas_college.append(file_name)
    elif "fas.harvard.edu-gmail.com" in file_name:
        fas_gmail.append(file_name)
    elif "college.harvard.edu-college.harvard.edu" in file_name:
        college_college.append(file_name)
    elif "college.harvard.edu-gmail.com" in file_name:
        college_gmail.append(file_name)
    elif "gmail.com-gmail.com" in file_name:
        gmail_gmail.append(file_name)
    else:
        print("SOMETHING'S WRONG!!! Breaking... ")
        break

# dp storage structure initialization
fas_fas_dp_edge_counts = []
fas_college_dp_edge_counts = []
fas_gmail_dp_edge_counts = []
college_college_dp_edge_counts = []
college_gmail_dp_edge_counts = []
gmail_gmail_dp_edge_counts = []

fas_fas_dp_node_counts = []
fas_college_dp_node_counts = []
fas_gmail_dp_node_counts = []
college_college_dp_node_counts = []
college_gmail_dp_node_counts = []
gmail_gmail_dp_node_counts = []

# compute dp average degree connectivity
def compute_avg_degree_connectivity(G, alpha, epsilon=1):
    # print the number of nodes in the graph
    n = G.number_of_nodes()
    e = G.number_of_edges()
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
        return

    # set bound to be D = n ** (1/alpha) for flow based mechanism
    D = n ** (1 / alpha)
    # calculate graph dp release for number of edges
    flow_based_dp_edges = graph_dp_edge_count(G, D, epsilon=1)

    # store results
    print("Flow-based graph dp count of edges: {flow_based_dp_edges}".format(flow_based_dp_edges=flow_based_dp_edges))

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

    return flow_based_dp_edges, dp_node_count

# alpha-decay value, must be greater than 1
alpha = 1.5
for i in range(len(fas_fas)):
    print("*"*80)
    G = pickle.load(open('./constructed-graphs/' + fas_fas[i] + '.pickle', 'rb'))
    flow_based_output = compute_avg_degree_connectivity(G, alpha)
    fas_fas_dp_edge_counts.append(flow_based_output[0])
    fas_fas_dp_node_counts.append(flow_based_output[1])

    G = pickle.load(open('./constructed-graphs/' + fas_college[i] + '.pickle', 'rb'))
    flow_based_output = compute_avg_degree_connectivity(G, alpha)
    fas_college_dp_edge_counts.append(flow_based_output[0])
    fas_college_dp_node_counts.append(flow_based_output[1])

    G = pickle.load(open('./constructed-graphs/' + fas_gmail[i] + '.pickle', 'rb'))
    flow_based_output = compute_avg_degree_connectivity(G, alpha)
    fas_gmail_dp_edge_counts.append(flow_based_output[0])
    fas_gmail_dp_node_counts.append(flow_based_output[1])

    G = pickle.load(open('./constructed-graphs/' + college_college[i] + '.pickle', 'rb'))
    flow_based_output = compute_avg_degree_connectivity(G, alpha)
    college_college_dp_edge_counts.append(flow_based_output[0])
    college_college_dp_node_counts.append(flow_based_output[1])


    G = pickle.load(open('./constructed-graphs/' + college_gmail[i] + '.pickle', 'rb'))
    flow_based_output = compute_avg_degree_connectivity(G, alpha)
    college_gmail_dp_edge_counts.append(flow_based_output[0])
    college_gmail_dp_node_counts.append(flow_based_output[1])

    G = pickle.load(open('./constructed-graphs/' + gmail_gmail[i] + '.pickle', 'rb'))
    flow_based_output = compute_avg_degree_connectivity(G, alpha)
    gmail_gmail_dp_edge_counts.append(flow_based_output[0])
    gmail_gmail_dp_node_counts.append(flow_based_output[1])


# compute averages by dividing dp sums by dp counts
fas_fas_dp_avg_connections = [2 * fas_fas_dp_edge_counts[i] / fas_fas_dp_node_counts[i] for i in range(len(fas_fas_dp_edge_counts))]
fas_college_dp_avg_connections = [2 * fas_college_dp_edge_counts[i] / fas_college_dp_node_counts[i] for i in range(len(fas_college_dp_edge_counts))]
fas_gmail_dp_avg_connections = [2 * fas_gmail_dp_edge_counts[i] / fas_gmail_dp_node_counts[i] for i in range(len(fas_gmail_dp_edge_counts))]
college_college_dp_avg_connections = [2 * college_college_dp_edge_counts[i] / college_college_dp_node_counts[i] for i in range(len(college_college_dp_edge_counts))]
college_gmail_dp_avg_connections = [2 * college_gmail_dp_edge_counts[i] / college_gmail_dp_node_counts[i] for i in range(len(college_gmail_dp_edge_counts))]
gmail_gmail_dp_avg_connections = [2 * gmail_gmail_dp_edge_counts[i] / gmail_gmail_dp_node_counts[i] for i in range(len(gmail_gmail_dp_edge_counts))]

# print results
print("*"*80)
print("DP average fas-fas connections: ")
print(fas_fas_dp_avg_connections)
print("*"*80)
print("DP average fas-college connections: ")
print(fas_college_dp_avg_connections)
print("*"*80)
print("DP average fas-gmail connections: ")
print(fas_gmail_dp_avg_connections)
print("*"*80)
print("DP average college-college connections: ")
print(college_college_dp_avg_connections)
print("*"*80)
print("DP average college-gmail connections: ")
print(college_gmail_dp_avg_connections)
print("*"*80)
print("DP average gmail-gmail connections: ")
print(gmail_gmail_dp_avg_connections)
