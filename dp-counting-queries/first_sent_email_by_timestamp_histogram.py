"""
Script to count the number of individuals who sent their first email by month, writes to disk.
"""
import pandas as pd
from opendp.mod import enable_features
enable_features("contrib")
from tqdm import tqdm
import json
import sys
import datetime
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

# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}


# create column transformation
col_trans = create_col_trans('first-email-timestamp', str, metadata)
# create the counting transformation
count_trans = create_count_trans(col_trans)
# create the counting measurement
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# construct timestamp bins
u1 = datetime.datetime.strptime("2000-01-01","%Y-%m-%d")
# delta of one month
d_w = datetime.timedelta(days=30.4)
u2 = u1 + d_w
timestamp_bins = [(u1, u2)]
for i in range(300):
    timestamp_bins.append((timestamp_bins[i][1], timestamp_bins[i][1] + d_w))


bin_counts = {}
min_date = '2025-01-01'

# find the dp count for each time bin
for i, bin in tqdm(enumerate(timestamp_bins)):
    bin_df = df[df['first-email-timestamp'] >= str(bin[0])]
    bin_df = bin_df[bin_df['first-email-timestamp'] < str(bin[1])]
    bin_counts[i] = count_meas(bin_df.to_csv())

# store the dictionary for a histogram with differentially private counts
f = open("./dp_first_email_histogram.txt", "w")
f.write(json.dumps(bin_counts))
f.close()
