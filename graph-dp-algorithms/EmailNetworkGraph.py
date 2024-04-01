"""
Email Network Graph object, used to create and visualize subgraphs from
tabular email data
"""
import time
import pickle
import numpy as np
import pandas as pd
import networkx as nx
from tqdm import tqdm
import matplotlib.pyplot as plt
from datetime import datetime
import sys
sys.path.append('../data-aggregation/')
from helpers import Extractor


# help from https://www.geeksforgeeks.org/visualize-graphs-in-python/
class EmailNetworkGraph:

    def __init__(self, email_df):
        self.n = 0
        self.num_edges = 0
        self.extractor = Extractor([], parent_dir=True)
        self.G = self.construct_graph(email_df)
        # node_shape options: 'so^>v<dph8'
        self.vis_config = {'cmap': plt.get_cmap('viridis'), 'font_size':10, 'node_shape':'h', 'node_size':150, 'alpha':0.6}

    # construct the graph from an input dataframe
    def construct_graph(self, email_df, verbose=False):
        # create nx graph object
        G = nx.Graph()

        # collect emails
        receiver_emails = set(list(email_df['to'].unique()))
        sender_emails = set(list(email_df['from'].unique()))
        all_email_addresses = receiver_emails | sender_emails

        if verbose:
            print('Creating graph nodes... ')

        # create all the nodes
        for email_address in all_email_addresses:
            G.add_node(email_address)
            # update number of nodes
            self.n += 1

        if verbose:
            print('Creating graph edges... ')

        # fill in all the edges
        for i, row in email_df.iterrows():
            edge = (row['to'], row['from'])
            G.add_edge(*edge)
            # update number of edges
            self.num_edges += 1

        return G


    # save graph to disk
    def save_graph(self, file_name=None):
        try:
            if file_name is None:
                file_name = str(datetime.now())[:10]
            s = time.time()
            pickle.dump(self.G, open('./constructed-graphs/' + file_name + '.pickle', 'wb'))
            e = time.time()
            t = round(e - s, 4)
            print("Successfully saved graph to ./constructed-graphs/" + file_name + ".pickle, took " + str(t) + " seconds.")
        except Exception as e:
            print("Could not save graph to pickle file! See exception below... ")
            print(e)


    # save a visualization of the graph to disk
    def savefig(self, file_name, vis_type=None):
        s = time.time()
        # make sure the nodes are colored appropriately before graphing
        self.addColor()

        # different formats for the graph plotting
        if vis_type is None:
            nx.draw(self.G, **self.vis_config)
        elif vis_type == 'spectral':
            nx.draw_spectral(self.G, **self.vis_config)
        elif vis_type == 'random':
            nx.draw_random(self.G, **self.vis_config)
        elif vis_type == 'spring':
            nx.draw_spring(self.G, **self.vis_config)
        elif vis_type == 'shell':
            nx.draw_shell(self.G, **self.vis_config)
        else:
            print("Unrecognized visualization type, unable to create graph visualization! Breaking... ")
            return

        if file_name is None:
            file_name = str(datetime.now())[:10]

        try:
            # nx.draw_networkx(G, font_size=10, node_shape='h', node_size=200, alpha=0.8)
            plt.savefig("./graph-images/" + file_name + ".png", format="PNG", dpi=300, bbox_inches="tight")
            e = time.time()
            t = round(e - s, 4)
            print("Successfully saved graph image to ./graph-images/" + file_name + ".png, took " + str(t) + " seconds. ")
        except Exception as e:
            print("Could not save graph visualization to png file! See exception below... ")
            print(e)


    # helper function to add colors to graph visualization
    def addColor(self):
        node_color_values = []
        for node in self.G.nodes():
            club_affiliation = self.extractor.extract_club_affiliation(node, node)
            if club_affiliation:
                node_color_values.append(1)
            else:
                node_color_values.append(0)
        self.vis_config['node_color'] = node_color_values
