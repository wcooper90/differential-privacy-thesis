"""
Plotting script for trends in total active users over time.
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# print(sorted(font_manager.get_font_names()))
csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})

first_email_data = None
# reading the data from the file
with open('../analysis/timestamp_histograms/dp_first_email_histogram.txt') as f:
    first_email_data = f.read()
last_email_data = None
# reading the data from the file
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

# get list of first and last email timestamps
months = first_email_df['month'][:-12]
first_email_timestamps = first_email_df['first-email-timestamp'][:-12]
last_email_timestamps = last_email_df['last-email-timestamp'][:-12]

# creating the chart
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
plt.plot(months, first_email_timestamps, linewidth = '1.3', color='maroon', alpha=0.85, label="New Members")
plt.plot(months, last_email_timestamps, linewidth = '1.3', color='maroon', alpha=0.47, label="Leaving Members")
plt.ylabel("No. of Individuals", fontsize=16, **csfont)
plt.title("Membership Change Over Time", fontsize=18, **csfont)
plt.legend(prop = {"family": 'cmr10' }, loc ="best")

# create custom xtick labels
xtick_labels = []
start_year = 2000
for i, month in enumerate(months):
    if i % 12 == 0:
        xtick_labels.append(str(start_year))
        start_year += 1
    else:
        xtick_labels.append("")

# configure ticks
plt.xticks(months, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)

# save figure
plt.savefig('../analysis/plots/dp_membership_over_time.png', dpi=300, bbox_inches="tight")
