"""
Script to calculate dp average content length over time, writes to disk.
"""
import pandas as pd
import numpy as np
import json
from tqdm import tqdm
from opendp.mod import enable_features
enable_features("contrib")
import datetime
import sys
sys.path.append('../data-aggregation/')
from csv_aggregation import full_email_df
from helpers import extract_affiliation
sys.path.append('../')
from transformations import *

# identify columns to read from batch email dataframes
column_names = ['first-email-timestamp',
                'last-email-timestamp',
                'avg-content-length',
                'affiliation']

# read individual's df from disk
df = pd.read_csv("../dataframes/full_individual_df.csv", usecols=column_names)
df = df.reset_index(drop=True)

# create timestamp bins of one month since Jan 2000
u1 = datetime.datetime.strptime("2000-01-01","%Y-%m-%d")
# delta of one month
d_w = datetime.timedelta(days=30.4)
u2 = u1 + d_w
timestamp_bins = [(u1, u2)]
# 300 months is 25 years
for i in range(300):
    timestamp_bins.append((timestamp_bins[i][1], timestamp_bins[i][1] + d_w))

# define counting transformations and measurements
# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}

# create column transformation
col_trans = create_col_trans('avg-content-length', str, metadata)
# create the counting transformation
count_trans = create_count_trans(col_trans)
# create the counting measurement, privacy budget of 0.5
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# domains we want to examine
domains = {'gmail.com': [], 'fas.harvard.edu': [], 'college.harvard.edu': []}

# initialize storage dictionaries
dp_counts = {k: [] for k in list(domains.keys())}
dp_avgs = {k: [] for k in list(domains.keys())}

# create a mean transformation; an upper bound of 3000 characters on average per person
# seems reasonable, from a public standpoint: each word on average is approx. 6 chars,
# so 3000 is about 500 words or about 2 double spaced pages
length_bounds = (0., 5000.)

# calculate average emails received by affiliation
# find the dp count for each topic for each month
for i, bin in tqdm(enumerate(timestamp_bins)):
    # filter by time bin (month granularity)
    time_binned_df = df[(df['first-email-timestamp'] >= str(bin[0])) & (df['last-email-timestamp'] < str(bin[1]))]
    for domain in domains.keys():
        # filter by domain of sender
        domain_df = time_binned_df[time_binned_df['affiliation'] == domain]
        # if there are no emails that satisfy these filters, skip
        if len(domain_df) == 0:
            dp_counts[domain].append(0)
            dp_avgs[domain].append(0)
            continue

        # dp count of the number of emails
        domain_dp_count = count_meas(domain_df.to_csv())
        # sum transformation on the columns
        sum_trans = create_sum_trans(length_bounds, col_trans)
        # sum measurement on the transformation, budget of 0.5
        sum_meas = make_meas(sum_trans, budget=0.5, max_contributions=1, verbose=False)
        # calculate the average by dividing by the dp number of entries
        domain_dp_avg_email_length = None
        if domain_dp_count == 0:
            domain_dp_avg_email_length = sum_meas(domain_df.to_csv()) / 1
        else:
            domain_dp_avg_email_length = sum_meas(domain_df.to_csv()) / domain_dp_count

        # store dp values
        dp_counts[domain].append(domain_dp_count)
        dp_avgs[domain].append(domain_dp_avg_email_length)


# store private data dictionary to disk
f = open("./dp_avg_content_length_over_time.txt", "w")
f.write(json.dumps(dp_avgs))
f.close()
f = open("./dp_counts_over_time.txt", "w")
f.write(json.dumps(dp_counts))
f.close()
