"""
Script to calculate dp average sentiment of emails by affiliation (email domain),
writes to disk.
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


columns = ['email',
            'affiliation',
            'avg-content-length',
            'first-email-timestamp',
            'last-email-timestamp',
            'avg-received-sub-neg',
            "avg-received-sub-neu",
            "avg-received-sub-pos",
            "avg-received-sub-com",
            "avg-sent-sub-neg",
            "avg-sent-sub-neu",
            "avg-sent-sub-pos",
            "avg-sent-sub-com",
            "avg-received-con-neg",
            "avg-received-con-neu",
            "avg-received-con-pos",
            "avg-received-con-com",
            "avg-sent-con-neg",
            "avg-sent-con-neu",
            "avg-sent-con-pos",
            "avg-sent-con-com",
            "sum-sent-con-semitic-wf",
            "sum-sent-con-crypto-wf",
            "sum-sent-sub-semitic-wf",
            "sum-sent-sub-crypto-wf",
            "num-club-affiliations",
            "num-emails-sent",
            "num-emails-received"
            ]

df = pd.read_csv("../dataframes/full_individual_df.csv", usecols=columns)

# grouped affiliation emails gathered from metadata scripts
affiliations = {}
with open('../metadata/harvard_email_affiliations.txt') as f:
    affiliations = json.loads(f.read())

# storage data structures
affiliation_com_dp_means = {k:0 for k in affiliations.keys()}
affiliation_neg_dp_means = {k:0 for k in affiliations.keys()}
affiliation_neu_dp_means = {k:0 for k in affiliations.keys()}
affiliation_pos_dp_means = {k:0 for k in affiliations.keys()}
affiliation_dp_counts = {k:0 for k in affiliations.keys()}

# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}
# global length bounds of compound sentiment. This is not an estimate.
length_bounds = (-1., 1.)


# create column transformations
com_col_trans = create_col_trans("avg-sent-con-com", str, metadata)
neg_col_trans = create_col_trans("avg-sent-con-neg", str, metadata)
neu_col_trans = create_col_trans("avg-sent-con-neu", str, metadata)
pos_col_trans = create_col_trans("avg-sent-con-pos", str, metadata)

# create the counting transformation
count_trans = create_count_trans(com_col_trans)
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
    com_mean_trans = create_mean_trans(length_bounds, aff_dp_count, com_col_trans, 0.)
    neg_mean_trans = create_mean_trans(length_bounds, aff_dp_count, neg_col_trans, 0.1)
    neu_mean_trans = create_mean_trans(length_bounds, aff_dp_count, neu_col_trans, 0.7)
    pos_mean_trans = create_mean_trans(length_bounds, aff_dp_count, pos_col_trans, 0.2)
    # create a mean measurement
    com_mean_meas = make_meas(com_mean_trans, budget=0.5, max_contributions=1, verbose=True)
    neg_mean_meas = make_meas(neg_mean_trans, budget=0.5, max_contributions=1, verbose=True)
    neu_mean_meas = make_meas(neu_mean_trans, budget=0.5, max_contributions=1, verbose=True)
    pos_mean_meas = make_meas(pos_mean_trans, budget=0.5, max_contributions=1, verbose=True)

    # calculate means
    com_dp_aff_mean = com_mean_meas(aff_df.to_csv())
    neg_dp_aff_mean = neg_mean_meas(aff_df.to_csv())
    neu_dp_aff_mean = neu_mean_meas(aff_df.to_csv())
    pos_dp_aff_mean = pos_mean_meas(aff_df.to_csv())

    # store results
    affiliation_com_dp_means[aff] = com_dp_aff_mean
    affiliation_neg_dp_means[aff] = neg_dp_aff_mean
    affiliation_neu_dp_means[aff] = neu_dp_aff_mean
    affiliation_pos_dp_means[aff] = pos_dp_aff_mean


# store the dictionaries for a histogram with differentially private counts
f = open("./dp_compound_sentiment_by_harvard_affiliation.txt", "w")
f.write(json.dumps(affiliation_com_dp_means))
f.close()
f = open("./dp_negative_sentiment_by_harvard_affiliation.txt", "w")
f.write(json.dumps(affiliation_neg_dp_means))
f.close()
f = open("./dp_neutral_sentiment_by_harvard_affiliation.txt", "w")
f.write(json.dumps(affiliation_neu_dp_means))
f.close()
f = open("./dp_positive_sentiment_by_harvard_affiliation.txt", "w")
f.write(json.dumps(affiliation_pos_dp_means))
f.close()
