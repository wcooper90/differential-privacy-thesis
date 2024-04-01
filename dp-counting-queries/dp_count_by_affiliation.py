"""
Script to calculate dp count of individuals by
email affiliation (domain), write to disk.
"""
import pandas as pd
from opendp.mod import enable_features
enable_features("contrib")
from tqdm import tqdm
import json
import sys
sys.path.append('../')
from opendp_helpers import *

columns = ['email', 'affiliation']
df = pd.read_csv("../dataframes/sent_received_length_df.csv", usecols=columns)
# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}
# create column transformation
col_trans = create_col_trans('email', str, metadata)
# create the counting transformation
count_trans = create_count_trans(col_trans)
# create the counting measurement
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

dp_counts = {}
# find all the affiliations: we can assume this is public knowledge
affiliations = df['affiliation'].unique()
# find the dp count for each affiliation
for aff in tqdm(affiliations):
    aff_df = df[df['affiliation'] == aff]
    dp_counts[aff] = count_meas(aff_df.to_csv())

# store the dictionary for a histogram with differentially private counts
f = open("./dp_sent_by_affiliation.txt", "w")
f.write(json.dumps(dp_counts))
f.close()
