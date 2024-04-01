"""
Script to calculate dp count of full number of emails sent, writes to disk.
"""
import pandas as pd
from opendp.mod import enable_features
import sys
sys.path.append('../data-aggregation/')
from csv_aggregation import create_full_pd
sys.path.append('../')
from opendp_helpers import *


# specify batch numbers. All emails are spread over 18 batches
batch_nums = [i for i in range(18)]
# specify the columns to examine. Because we are only looking for number of entries, any column will do
column_names = ['to']
# use helper function to create full dataframe
df = create_full_pd(batch_nums, column_names, parent_dir=True)
# reset index
df = df.reset_index(drop=True)

# each email contributes only one email
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}

# create counting transformation for num_emails_received
col_trans = create_col_trans("to", str, metadata)
# create the counting measurement function
count_trans = create_count_trans(col_trans)
# automatically determine laplace scale based on provided budget
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# run function
dp_count = count_meas(df.to_csv())
# dp count
print('Private release of emails: ' + str(dp_count))
