"""
Script to calculate dp sum of the number of emails sent by
email affiliation (domain), writes to disk.
"""
import pandas as pd
from opendp.mod import enable_features
enable_features("contrib")
from tqdm import tqdm
import json
import sys
sys.path.append('../')
from opendp_helpers import *


columns = ['email', 'affiliation', 'num_emails_sent']
df = pd.read_csv("../dataframes/sent_received_length_df.csv", usecols=columns)
# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}
# create column transformation
col_trans = create_col_trans('num_emails_sent', str, metadata)
# create a sum transformation; an upper bound of sending 1000 emails through the lists
# seems reasonable, from a public standpoint.
length_bounds = (0., 1000.)

# sum transformation on the columns
sum_trans = create_sum_trans(length_bounds, col_trans)
# sum measurement on the transformation, budget of 0.5
sum_meas = make_meas(sum_trans, budget=0.5, max_contributions=1)
dp_sums = {}
# find all the affiliations: we can assume this is public knowledge
affiliations = df['affiliation'].unique()
# find the dp count for each affiliation
for aff in tqdm(affiliations):
    aff_df = df[df['affiliation'] == aff]
    dp_sums[aff] = int(sum_meas(aff_df.to_csv()))

# store the dictionary for a histogram with differentially private counts
f = open("./dp_sum_sent_by_affiliation.txt", "w")
f.write(json.dumps(dp_sums))
f.close()
