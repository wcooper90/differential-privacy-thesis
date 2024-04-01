"""
Plotting script for average content length over time by affiliation (email domain)
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager


csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})

dp_avg_length_data = None
# reading the data from the file
with open('../analysis/content_length_over_time/dp_avg_content_length_over_time.txt') as f:
    dp_avg_length_data = f.read()
f.close()
dp_count_data = None
# reading the data from the file
with open('../analysis/content_length_over_time/dp_counts_over_time.txt') as f:
    dp_count_data = f.read()
f.close()

# make the plots more readable by slicing (2008 - 2016) off first 8 years and last 8 years
truncate_x_early_years = 0
truncate_y_later_years = 2
months_per_year = 12
start_slice = months_per_year * truncate_x_early_years
end_slice = -(months_per_year * truncate_y_later_years)

# load string as dictionary, define y axis variables
dp_avgs = json.loads(dp_avg_length_data)
dp_college_avgs = dp_avgs['college.harvard.edu'][start_slice:end_slice]
dp_fas_avgs = dp_avgs['fas.harvard.edu'][start_slice:end_slice]
dp_gmail_avgs = dp_avgs['gmail.com'][start_slice:end_slice]

dp_counts = json.loads(dp_count_data)
dp_college_counts = dp_counts['college.harvard.edu'][start_slice:end_slice]
dp_fas_counts = dp_counts['fas.harvard.edu'][start_slice:end_slice]
dp_gmail_counts = dp_counts['gmail.com'][start_slice:end_slice]

# x axis variable
months = list(np.arange(len(true_gmail_counts)))
# create custom xtick labels
xtick_labels = []
start_year = 2000 + truncate_x_early_years
end_year = 2024 - truncate_y_later_years
year_counter = start_year
for i, month in enumerate(months):
    if i % 12 == 0:
        xtick_labels.append(str(year_counter))
        year_counter += 1
    else:
        xtick_labels.append("")


# creating the chart
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
# plot
plt.plot(months, dp_college_counts, linewidth='2', color='#96031A', alpha=0.92, label='college')
plt.plot(months, dp_fas_counts, linewidth='2', color='#16041F', alpha=0.92, label='fas')
plt.plot(months, dp_gmail_counts, linewidth='2', color='#6D676E', alpha=0.92, label='gmail')
# titling and axis labeling
plt.ylabel("Count", fontsize=16, **csfont)
plt.title("DP Active Members Over Time", fontsize=18, **csfont)
# fill in legend
plt.legend(prop = {"family": 'cmr10' }, loc ="best")
# customize tick display
plt.xticks(months, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)
# save figure
plt.savefig('../analysis/content_length_over_time/dp_count_by_affiliation_' + str(start_year) + '-' + str(end_year) +'.png', dpi=300, bbox_inches="tight")
# clear figure
fig.clf()

# creating the chart
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
# plot
plt.plot(months, dp_college_avgs, linewidth='2', color='#96031A', alpha=0.92, label='college')
plt.plot(months, dp_fas_avgs, linewidth='2', color='#16041F', alpha=0.92, label='fas')
plt.plot(months, dp_gmail_avgs, linewidth='2', color='#6D676E', alpha=0.92, label='gmail')
# titling and axis labeling
plt.ylabel("Average Length of Emails (in No. Characters)", fontsize=16, **csfont)
plt.title("DP Average Email Length by Email Domain Over Time", fontsize=18, **csfont)
# fill in legend
plt.legend(prop = {"family": 'cmr10' }, loc ="best")
# customize tick display
plt.xticks(months, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)
# save figure
plt.savefig('../analysis/content_length_over_time/dp_avg_content_length_' + str(start_year) + '-' + str(end_year) +'.png', dpi=300, bbox_inches="tight")
# clear figure
fig.clf()
