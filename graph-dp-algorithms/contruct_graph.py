"""
Script to create subgraph network objects from the tabular individually-indexed dataframe.
"""
import numpy as np
import pandas as pd
import time
import pickle
from tqdm import tqdm
from datetime import datetime
from EmailNetworkGraph import EmailNetworkGraph
import sys
sys.path.append('../data-aggregation/')
from csv_aggregation import full_email_df


num_lists = 18
email_count_limit = float("inf")
batch_nums = [i for i in range(num_lists)]
# columns of interest
email_column_names = ['id', 'to', 'from', 'to-affiliation', 'from-affiliation', 'timestamp']
# construct full email df
s = time.time()
df = full_email_df(batch_nums, email_column_names, parent_dir=True, email_count_limit=email_count_limit)
e = time.time()
t = round(e - s, 4)
print("Reading email csvs took " + str(t) + " seconds.")
# subgraphs we are interested in
connection_pairings = [('fas.harvard.edu', 'fas.harvard.edu'),
                        ('fas.harvard.edu', 'college.harvard.edu'),
                        ('fas.harvard.edu', 'gmail.com'),
                        ('college.harvard.edu', 'college.harvard.edu'),
                        ('college.harvard.edu', 'gmail.com'),
                        ('gmail.com', 'gmail.com')]

# further filter subgraph by timebin
u1 = '2000'
u2 = '2001'
timestamp_bins = [('2000', '2004'),('2004', '2008'), ('2008', '2012'), ('2012', '2016'), ('2016', '2020'), ('2020', '2024')]
file_names = []
for bin in tqdm(timestamp_bins):
    time_binned_df = df[(df['timestamp'] >= bin[0]) & (df['timestamp'] < bin[1])]
    for pairing in connection_pairings:
        paired_df = None
        if pairing[0] == pairing[1]:
            paired_df = time_binned_df[(time_binned_df['to-affiliation'] == pairing[0]) & (time_binned_df['from-affiliation'] == pairing[1])]
        else:
            forward_paired_df = time_binned_df[(time_binned_df['to-affiliation'] == pairing[0]) & (time_binned_df['from-affiliation'] == pairing[1])]
            backward_paired_df = time_binned_df[(time_binned_df['to-affiliation'] == pairing[1]) & (time_binned_df['from-affiliation'] == pairing[0])]
            frames = [forward_paired_df, backward_paired_df]
            paired_df = pd.concat(frames)

        network_graph = EmailNetworkGraph(paired_df)
        file_name = bin[0] + '-' + bin[1] + '--' + str(pairing[0]) + '-' + str(pairing[1])
        network_graph.save_graph(file_name=file_name)
        file_names.append(file_name)

# filter df
df = df[(df['timestamp'] > '2020-01-01') & (df['timestamp'] < '2024-01-01')]
# create network graph
s = time.time()
network_graph = EmailNetworkGraph(df)
e = time.time()
t = round(e - s, 4)
print("Constructing the graph took " + str(t) + " seconds.")
# construct file name for visualization and pickle file based on number of lists included
file_name = "2020_to_2024"
# only produce the visualization if there are fewer than 100,000 nodes
if num_lists * email_count_limit < 100000:
    network_graph.savefig(file_name=file_name, vis_type=None)
# always save the graph to a pickle file
network_graph.save_graph(file_name=file_name)
