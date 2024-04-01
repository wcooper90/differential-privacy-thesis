"""
Script to count the number of individuals who sent their first email by week
and by affiliation, writes to disk.
"""
import pandas as pd
from opendp.mod import enable_features
enable_features("contrib")
from tqdm import tqdm
import json
import datetime
import sys
sys.path.append('../')
from opendp_helpers import *


columns = ['email', 'affiliation', 'first-email-timestamp']
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

u1 = datetime.datetime.strptime("2000-01-01","%Y-%m-%d")
# delta of one week
d_w = datetime.timedelta(days=30.4)
u2 = u1 + d_w
timestamp_bins = [(u1, u2)]
for i in range(300):
    timestamp_bins.append((timestamp_bins[i][1], timestamp_bins[i][1] + d_w))

domains = ['college.harvard.edu', 'fas.harvard.edu', 'gmail.com', 'hcs.harvard.edu']
dp_counts = {k: [] for k in domains}

# find the dp count for each affiliation
for i, bin in tqdm(enumerate(timestamp_bins)):
    # filter on first and last sent emails
    time_binned_df = df[(df['first-email-timestamp'] >= str(bin[0])) & (df['first-email-timestamp'] < str(bin[1]))]
    for domain in domains:
        domain_df = time_binned_df[time_binned_df['affiliation'] == domain]
        # find dp count
        dp_counts[domain].append(count_meas(domain_df.to_csv()))


store the dictionary for a histogram with differentially private counts
f = open("./dp_first_email_by_affiliation.txt", "w")
f.write(json.dumps(dp_counts))
f.close()
