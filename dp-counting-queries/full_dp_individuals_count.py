"""
Script to calculate dp count of full number of individuals, writes to disk.
"""
import pandas as pd
from opendp.mod import enable_features
enable_features("contrib")
import sys
sys.path.append('../')
from opendp_helpers import *

df = pd.read_csv("../dataframes/sent_received_length_df.csv")
# for some reason a new index column appears after reading from disk, but just remove it
df = df.drop('Unnamed: 0', axis=1)
# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}

# create counting transformation for individuals
col_trans = create_col_trans("email", str, metadata)
# create the counting measurement function
count_trans = create_count_trans(col_trans)
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# run function
dp_count = count_meas(df.to_csv())
# dp count
print('Private release of individual count: ' + str(dp_count))
