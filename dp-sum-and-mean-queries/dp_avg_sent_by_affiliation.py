"""
Script to calculate dp average of the number of emails sent by
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
# create the counting transformation
count_trans = create_count_trans(col_trans)
# create the counting measurement
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# define an upper bound of sending 1000 emails through the lists
# seems like a reasonable public guestimate
length_bounds = (1., 1000.)

dp_means = {}
# find all the affiliations: we can assume this is public knowledge
affiliations = df['affiliation'].unique()


# sometimes segmentation fault will occur during this loop. Keep a counter to
# keep track of where to start on the next run
counter = 0
# find the dp avg for each affiliation
for aff in tqdm(affiliations):
    aff_df = df[df['affiliation'] == aff]
    # use find the private count of members in the affiliation first
    aff_count = count_meas(aff_df.to_csv())
    # create a mean transformation after the dp_count has been calculated
    mean_trans = create_mean_trans(length_bounds, aff_count, col_trans, 42.)
    # create mean measurement with epsilong budget of 0.5
    mean_meas = make_meas(mean_trans, budget=0.5, max_contributions=1, verbose=False)
    # calculate differentially private mean
    # the epsilon expentidure on this operation is 0.5 + 0.5 = 1
    dp_mean = round(mean_meas(aff_df.to_csv()), 3)
    dp_means[aff] = round(mean_meas(aff_df.to_csv()), 3)
    # increment
    counter += 1


# store the dictionary for a histogram with differentially private counts
f = open("./dp_avg_sent_by_affiliation.txt", "w")
f.write(json.dumps(dp_means))
f.close()
