"""
Script to calculate the number of emails sent by topic and by month, writes to disk.
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
from csv_aggregation import create_full_pd
sys.path.append('../')
from opendp_helpers import *


# code taken from ../plotting/plot_active_users_over_time.py
def get_active_users_by_month():
    # reading info about first and last emails sent from disk
    first_email_data = None
    with open('../analysis/timestamp_histograms/dp_first_email_histogram.txt') as f:
        first_email_data = f.read()
    last_email_data = None
    with open('../analysis/timestamp_histograms/dp_last_email_histogram.txt') as f:
        last_email_data = f.read()
    # load string as dictionary
    js = json.loads(first_email_data)
    # convert to dataframe
    first_email_df = pd.DataFrame(js.items())
    # appropriatly rename columns
    first_email_df = first_email_df.rename(columns={0: 'month', 1: 'first-email-timestamp'})
    # load string as dictionary
    js = json.loads(last_email_data)
    # convert to dataframe
    last_email_df = pd.DataFrame(js.items())
    # appropriatly rename columns
    last_email_df = last_email_df.rename(columns={0: 'month', 1: 'last-email-timestamp'})
    # use the 'month' index from df as a list of months
    months = first_email_df['month']
    # get full list of first and last email timestamps
    first_email_timestamps = first_email_df['first-email-timestamp']
    last_email_timestamps = last_email_df['last-email-timestamp']
    # create a list of cumulative first emails and last emails by month
    cumsum_emails_first = list(np.cumsum(first_email_timestamps))
    cumsum_emails_last = list(np.cumsum(last_email_timestamps))
    # active users is cumulative first emails - cumulative last emails at any given point in time
    active_users = [num_first - num_last for num_first, num_last in zip(cumsum_emails_first, cumsum_emails_last)]
    return active_users

# get a list of dp active users per month since 2000
active_users_by_month = get_active_users_by_month()

# identify columns to read from batch email dataframes
column_names = ["timestamp",
                "topic"]
# specify batch numbers. All emails are spread over 18 batches
batch_nums = [i for i in range(18)]
# use helper function to create full dataframe
df = full_email_df(batch_nums, column_names, parent_dir=True)
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

# create column transformation, any column will do because it's for a count measurement
col_trans = create_col_trans('timestamp', str, metadata)
# create the counting transformation
count_trans = create_count_trans(col_trans)
# create the counting measurement, privacy budget of 0.5
count_meas = make_meas(count_trans, budget=0.5, max_contributions=1)

# initialize private data arrays
dp_arts_emails_by_month = []
dp_athletics_emails_by_month = []
dp_culture_emails_by_month = []
dp_misc_emails_by_month = []
dp_preprofessional_emails_by_month = []
dp_political_emails_by_month = []
dp_service_emails_by_month = []
# these dp counts will be normalized by the number of active users in that month
normalized_dp_arts_emails_by_month = []
normalized_dp_athletics_emails_by_month = []
normalized_dp_culture_emails_by_month = []
normalized_dp_misc_emails_by_month = []
normalized_dp_preprofessional_emails_by_month = []
normalized_dp_political_emails_by_month = []
normalized_dp_service_emails_by_month = []

# find the dp count for each topic for each month
for i, bin in tqdm(enumerate(timestamp_bins)):
    # filter by time bin (month granularity)
    time_binned_df = df[(df['timestamp'] >= str(bin[0])) & (df['timestamp'] < str(bin[1]))]
    """
    Topic mappings from ../data-aggregation/helpers.py:
    {'arts': 0, 'athletics': 1, 'culture': 2,
    'miscellaneous': 3, 'politics': 4, 'preprofessional': 5, 'service': 6}
    """
    # filtered df for each of the topics
    arts_df = time_binned_df[time_binned_df['topic'] == 0]
    athletics_df = time_binned_df[time_binned_df['topic'] == 1]
    culture_df = time_binned_df[time_binned_df['topic'] == 2]
    misc_df = time_binned_df[time_binned_df['topic'] == 3]
    political_df = time_binned_df[time_binned_df['topic'] == 4]
    preprofessional_df = time_binned_df[time_binned_df['topic'] == 5]
    service_df = time_binned_df[time_binned_df['topic'] == 6]

    # create a private count for each of the topics
    dp_arts_count = count_meas(arts_df.to_csv())
    dp_athletics_count = count_meas(athletics_df.to_csv())
    dp_culture_count = count_meas(culture_df.to_csv())
    dp_misc_count = count_meas(misc_df.to_csv())
    dp_political_count = count_meas(political_df.to_csv())
    dp_preprofessional_count = count_meas(preprofessional_df.to_csv())
    dp_service_count = count_meas(service_df.to_csv())

    # append the private count to storage
    dp_arts_emails_by_month.append(dp_arts_count)
    dp_athletics_emails_by_month.append(dp_athletics_count)
    dp_culture_emails_by_month.append(dp_culture_count)
    dp_misc_emails_by_month.append(dp_misc_count)
    dp_political_emails_by_month.append(dp_political_count)
    dp_preprofessional_emails_by_month.append(dp_preprofessional_count)
    dp_service_emails_by_month.append(dp_service_count)

    # get the active number of email list users this month
    active_users_this_month = active_users_by_month[i]

    # normalize the number of emails of each topic by the number of active users each month
    # and append to storage
    normalized_dp_arts_emails_by_month.append(dp_arts_count / active_users_this_month)
    normalized_dp_athletics_emails_by_month.append(dp_athletics_count / active_users_this_month)
    normalized_dp_culture_emails_by_month.append(dp_culture_count / active_users_this_month)
    normalized_dp_misc_emails_by_month.append(dp_misc_count / active_users_this_month)
    normalized_dp_political_emails_by_month.append(dp_political_count / active_users_this_month)
    normalized_dp_preprofessional_emails_by_month.append(dp_preprofessional_count / active_users_this_month)
    normalized_dp_service_emails_by_month.append(dp_service_count / active_users_this_month)

# dictionaries to write to json
dp_counts = {}
normalized_dp_counts = {}

# fill in dictionaries
dp_counts['arts'] = dp_arts_emails_by_month
dp_counts['athletics'] = dp_athletics_emails_by_month
dp_counts['culture'] = dp_culture_emails_by_month
dp_counts['miscellaneous'] = dp_misc_emails_by_month
dp_counts['politics'] = dp_political_emails_by_month
dp_counts['preprofessional'] = dp_preprofessional_emails_by_month
dp_counts['service'] = dp_service_emails_by_month
normalized_dp_counts['arts'] = normalized_dp_arts_emails_by_month
normalized_dp_counts['athletics'] = normalized_dp_athletics_emails_by_month
normalized_dp_counts['culture'] = normalized_dp_culture_emails_by_month
normalized_dp_counts['miscellaneous'] = normalized_dp_misc_emails_by_month
normalized_dp_counts['politics'] = normalized_dp_political_emails_by_month
normalized_dp_counts['preprofessional'] = normalized_dp_preprofessional_emails_by_month
normalized_dp_counts['service'] = normalized_dp_service_emails_by_month

# store the dictionaries with differentially private counts as json files
f = open("./dp_count_email_by_topic_and_month.txt", "w")
f.write(json.dumps(dp_counts))
f.close()
f = open("./normalized_dp_count_email_by_topic_and_month.txt", "w")
f.write(json.dumps(normalized_dp_counts))
f.close()
