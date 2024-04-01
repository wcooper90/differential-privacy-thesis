"""
Script to calculate dp average sentiment of parent emails by response time
category, prints but does not write to disk. 
"""
import os
import pandas as pd
import numpy as np
from tqdm import tqdm
import json
import sys
from diffprivlib import tools
import time
import math
sys.path.append('../')
from opendp_helpers import *


# columns of interest
columns = ['id',  # email id
            'parent', # email's parent chain id, if applicable
            'to',  # receiving email
            'from', # sender email
            'timestamp', # timestamp
            'affiliation', # club affiliation, if either sender or receiver is a club email
            'to-affiliation', # email domain of receiver
            'from-affiliation', # email domain of sender
            'sub-neg', # negative sentiment in subject
            'sub-neu', # neutral sentiment in subject
            'sub-pos', # positive sentiment in subject
            'sub-com', # compound sentiment in subject
            'con-neg', # negative sentiment in content
            'con-neu', # neutral sentiment in content
            'con-pos', # positive sentiment in content
            'con-com', # compound sentiment in content
            'topic', # email topic
            'response-time',
            'parent-sub-neg',
            'parent-sub-neu',
            'parent-sub-pos',
            'parent-sub-com',
            'parent-con-neg',
            'parent-con-neu',
            'parent-con-pos',
            'parent-con-com'
            ]

# response time dataframes for a randomly selected 3 out of 18 batches of total emails
df_1 = pd.read_csv("../dataframes/response_time_df_6.csv", usecols=columns)
df_2 = pd.read_csv("../dataframes/response_time_df_9.csv", usecols=columns)
df_3 = pd.read_csv("../dataframes/response_time_df_12.csv", usecols=columns)
# concatenate response time dataframes
df = pd.concat([df_1, df_2], ignore_index=True)
df = pd.concat([df, df_3], ignore_index=True)

# get all of the root email ids, denoted by nan value in parent column
parent_email_df = df[df['parent'].apply(lambda x: isinstance(x, float))]
root_emails = parent_email_df['id'].tolist()
root_emails = {id: [] for id in root_emails}

# filter df to only include first degree responses to parent emails
response_df = df[df['parent'].isin(list(root_emails.keys()))]

# create a list of responses for each parent
for i, row in response_df.iterrows():
    root_emails[row['parent']].append(i)

# randomly select one email out of the list of responses to analyze
selected_random_parent_indecies = {parent: None for parent in list(root_emails.keys())}
for key in root_emails.keys():
    selected_random_parent_indecies[key] = np.random.choice(root_emails[key])

# categorical time bins
time_bins = [1, 2, 3, 4, 5, 6]

# each email can only contribute one independent response
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}
# length bounds of compound sentiment. This is not an estimate.
length_bounds = (-1., 1.)


# create column transformation for count
id_col_trans = create_col_trans("id", str, metadata)
# column transformation for mean parent sentiment
parent_sentiment_trans = create_col_trans('parent-con-com', str, metadata)

# create the counting transformation
count_trans = create_count_trans(id_col_trans)
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# storage data structures
dp_binned_avg_sentiments = {k:0 for k in time_bins}
dp_binned_std_sentiments = {k:0 for k in time_bins}
dp_binned_counts = {k:0 for k in time_bins}


# calculate average emails received by affiliation
for time_bin in time_bins:

    # filter by response time category
    time_binned_df = df[df['response-time'] == time_bin]

    # define count measurement and apply it
    dp_count = count_meas(time_binned_df.to_csv())
    dp_binned_counts[time_bin] = dp_count

    # calculate differentially private standard deviation via IBM's diffprivlib library
    parent_sentiments = time_binned_df['parent-con-com'].tolist()
    dp_parent_sentiments_std = tools.std(parent_sentiments, epsilon=0.5, bounds=length_bounds)
    dp_binned_std_sentiments[time_bin] = dp_parent_sentiments_std

    # compound mean sentiment transformations/measurements
    com_mean_trans = create_mean_trans(length_bounds, dp_count, parent_sentiment_trans, 0.)
    com_mean_meas = make_meas(com_mean_trans, budget=0.5, max_contributions=1, verbose=True)
    # calculate means
    dp_parent_sentiment_mean = com_mean_meas(time_binned_df.to_csv())
    dp_binned_avg_sentiments[time_bin] = dp_parent_sentiment_mean


print(dp_binned_avg_sentiments)
print(dp_binned_std_sentiments)
print(dp_binned_counts)
