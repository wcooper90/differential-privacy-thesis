"""
Plotting script for dp count of active users over time.
"""
import pandas as pd
from opendp.mod import enable_features
enable_features("contrib")
from tqdm import tqdm
import json
import datetime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
import sys
sys.path.append('../')
from opendp_helpers import *



first_email_data = None
# reading the data from the file
with open('../analysis/timestamp_histograms/true_first_email_histogram.txt') as f:
    first_email_data = f.read()
last_email_data = None
# reading the data from the file
with open('../analysis/timestamp_histograms/true_last_email_histogram.txt') as f:
    last_email_data = f.read()
first_email_by_affiliation_data = None
# reading the data from the file
with open('../analysis/timestamp_histograms/true_first_email_by_affiliation.txt') as f:
    first_email_by_affiliation_data = f.read()
last_email_by_affiliation = None
# reading the data from the file
with open('../analysis/timestamp_histograms/true_last_email_by_affiliation.txt') as f:
    last_email_by_affiliation = f.read()

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

first_email_counts = json.loads(first_email_by_affiliation_data)
college_first_counts = first_email_counts['college.harvard.edu'][:-12]
fas_first_counts = first_email_counts['fas.harvard.edu'][:-12]
gmail_first_counts = first_email_counts['gmail.com'][:-12]

last_email_counts = json.loads(last_email_by_affiliation)
college_last_counts = last_email_counts['college.harvard.edu'][:-12]
fas_last_counts = last_email_counts['fas.harvard.edu'][:-12]
gmail_last_counts = last_email_counts['gmail.com'][:-12]


# create a list of cumulative first emails and last emails for college emails
cumsum_emails_first_college = list(np.cumsum(college_first_counts))
cumsum_emails_last_college = list(np.cumsum(college_last_counts))
# active users is cumulative first emails - cumulative last emails at any given point in time
active_college_users = [num_first - num_last for num_first, num_last in zip(cumsum_emails_first_college, cumsum_emails_last_college)]

# create a list of cumulative first emails and last emails for fas emails
cumsum_emails_first_fas = list(np.cumsum(fas_first_counts))
cumsum_emails_last_fas = list(np.cumsum(fas_last_counts))
# active users is cumulative first emails - cumulative last emails at any given point in time
active_fas_users = [num_first - num_last for num_first, num_last in zip(cumsum_emails_first_fas, cumsum_emails_last_fas)]

# create a list of cumulative first emails and last emails for gmail emails
cumsum_emails_first_gmail = list(np.cumsum(gmail_first_counts))
cumsum_emails_last_gmail = list(np.cumsum(gmail_last_counts))
# active users is cumulative first emails - cumulative last emails at any given point in time
active_gmail_users = [num_first - num_last for num_first, num_last in zip(cumsum_emails_first_gmail, cumsum_emails_last_gmail)]

# get list of first and last email timestamps
months = first_email_df['month']
first_email_timestamps = first_email_df['first-email-timestamp']
last_email_timestamps = last_email_df['last-email-timestamp']

# create a list of cumulative first emails and last emails
cumsum_emails_first = list(np.cumsum(first_email_timestamps))[:-12]
cumsum_emails_last = list(np.cumsum(last_email_timestamps))[:-12]
# active users is cumulative first emails - cumulative last emails at any given point in time
active_users = [num_first - num_last for num_first, num_last in zip(cumsum_emails_first, cumsum_emails_last)]


# add noise proportional to sensitivity of bin counting operation
epsilon = 1
num_bins = 12 * 24 # = 288
noise_scale = num_bins / epsilon

dp_active_user_count = []
dp_active_college_users = []
dp_active_fas_users = []
dp_active_gmail_users = []

# add noise calibrated to 288 bins to the exact values
for val in active_users:
    dp_active_user_count.append(val + np.random.laplace(scale=noise_scale))
for val in active_gmail_users:
    dp_active_gmail_users.append(val + np.random.laplace(scale=noise_scale))
for val in active_fas_users:
    dp_active_fas_users.append(val + np.random.laplace(scale=noise_scale))
for val in active_college_users:
    dp_active_college_users.append(val + np.random.laplace(scale=noise_scale))

# plotting
csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})


# creating the chart
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
# plot
plt.plot(months[:-12], dp_active_user_count, linewidth = '2', color='maroon', alpha=0.73, label="All Emails")
plt.plot(months[:-12], dp_active_college_users, linewidth = '2', color='#16041F', alpha=0.73, label="college.harvard.edu")
plt.plot(months[:-12], dp_active_gmail_users, linewidth = '2', color='#099B76', alpha=0.73, label="gmail.com")
plt.plot(months[:-12], dp_active_fas_users, linewidth = '2', color='#450A80', alpha=0.73, label="fas.harvard.edu")


# plt.ylabel("No. of Active Email Addresses", fontsize=16, **csfont)
plt.title("Active Email Addresses Over Time", fontsize=18, **csfont)

# fill in legend
plt.legend(prop = {"family": 'cmr10' }, loc ="best")


# create custom xtick labels
xtick_labels = []
start_year = 2000
for i, month in enumerate(months[:-12]):
    if i % 12 == 0:
        xtick_labels.append(str(start_year))
        start_year += 1
    else:
        xtick_labels.append("")

# customize tick display
plt.xticks(months[:-12], xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)
plt.ylim(-1500, 16000)


# save figure
plt.savefig('./dp_active_users_over_time_by_affiliation.png', dpi=300, bbox_inches="tight")
