"""
Script to calculate dp average sent content length of individuals by
affiliation (email domain), prints and writes to disk. 
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
import sys
sys.path.append('../')
from opendp_helpers import *


columns = ['email', 'affiliation', 'avg-content-length']
df = pd.read_csv("../dataframes/full_individual_df.csv", usecols=columns)

# grouped affiliation emails gathered from metadata scripts
affiliations = {}
with open('../metadata/harvard_email_affiliations.txt') as f:
    affiliations = json.loads(f.read())

affiliation_content_length_dp_means = {k:0 for k in affiliations.keys()}
affiliation_dp_counts = {k:0 for k in affiliations.keys()}

# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}
# length bounds of compound sentiment. This is not an estimate.
length_bounds = (0., 10000.)

# create column transformations
col_trans = create_col_trans("avg-content-length", str, metadata)
# create the counting transformation
count_trans = create_count_trans(col_trans)
# create the counting measurement function
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# calculate average emails received by affiliation
for aff in tqdm(affiliations.keys()):
    affiliation_email_set = affiliations[aff]
    print("*"*20 + aff + "*"*20)
    aff_df = df[df['affiliation'].isin(affiliation_email_set)]

    # calculate a count
    aff_dp_count = count_meas(aff_df.to_csv())
    affiliation_dp_counts[aff] = aff_dp_count

    # create a mean transformation
    mean_trans = create_mean_trans(length_bounds, aff_dp_count, col_trans, 100.)
    mean_meas = make_meas(mean_trans, budget=0.5, max_contributions=1, verbose=True)
    # calculate means
    dp_aff_mean = mean_meas(aff_df.to_csv())
    # store results
    affiliation_content_length_dp_means[aff] = dp_aff_mean


# print the dp means
print("positive dp means: ")
print(affiliation_content_length_dp_means)

# print the dp counts
print("dp counts: ")
print(affiliation_dp_counts)

# store the dictionary for a histogram with differentially private counts
f = open("./dp_avg_content_length_by_harvard_affiliation.txt", "w")
f.write(json.dumps(affiliation_content_length_dp_means))
f.close()
