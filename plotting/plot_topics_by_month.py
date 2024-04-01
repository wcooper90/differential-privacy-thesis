"""
Plotting script for number of emails by topic over time, by month.
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager


csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})

dp_count_topics_data = None
# reading the data from the file
with open('../analysis/email_topics/dp_count_email_by_topic_and_month.txt') as f:
    dp_count_topics_data = f.read()
f.close()
normalized_dp_count_topics_data = None
# reading the data from the file
with open('../analysis/email_topics/normalized_dp_count_email_by_topic_and_month.txt') as f:
    normalized_dp_count_topics_data = f.read()
f.close()

# make the plots more readable by slicing (2008 - 2016) off first 8 years and last 8 years
truncate_x_early_years = 1
truncate_y_later_years = 16
months_per_year = 12
start_slice = months_per_year * truncate_x_early_years
end_slice = -(months_per_year * truncate_y_later_years)

# load string as dictionary, define y axis variables
dp_topic_counts_dict = json.loads(dp_count_topics_data)
dp_arts_emails_by_month = dp_topic_counts_dict['arts'][start_slice:end_slice]
dp_athletics_emails_by_month = dp_topic_counts_dict['athletics'][start_slice:end_slice]
dp_culture_emails_by_month = dp_topic_counts_dict['culture'][start_slice:end_slice]
dp_misc_emails_by_month = dp_topic_counts_dict['miscellaneous'][start_slice:end_slice]
dp_preprofessional_emails_by_month = dp_topic_counts_dict['politics'][start_slice:end_slice]
dp_political_emails_by_month = dp_topic_counts_dict['preprofessional'][start_slice:end_slice]
dp_service_emails_by_month = dp_topic_counts_dict['service'][start_slice:end_slice]

# normalized dp counts
normalized_dp_topic_counts_dict = json.loads(normalized_dp_count_topics_data)
normalized_dp_arts_emails_by_month = normalized_dp_topic_counts_dict['arts'][start_slice:end_slice]
normalized_dp_athletics_emails_by_month = normalized_dp_topic_counts_dict['athletics'][start_slice:end_slice]
normalized_dp_culture_emails_by_month = normalized_dp_topic_counts_dict['culture'][start_slice:end_slice]
normalized_dp_misc_emails_by_month = normalized_dp_topic_counts_dict['miscellaneous'][start_slice:end_slice]
normalized_dp_preprofessional_emails_by_month = normalized_dp_topic_counts_dict['politics'][start_slice:end_slice]
normalized_dp_political_emails_by_month = normalized_dp_topic_counts_dict['preprofessional'][start_slice:end_slice]
normalized_dp_service_emails_by_month = normalized_dp_topic_counts_dict['service'][start_slice:end_slice]

# x axis variable
months = list(np.arange(len(normalized_dp_service_emails_by_month)))
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
plt.plot(months, dp_arts_emails_by_month, linewidth='1.6', color='#96031A', alpha=0.92, label='Arts')
plt.plot(months, dp_athletics_emails_by_month, linewidth='1.6', color='#16041F', alpha=0.92, label='Athletics')
plt.plot(months, dp_culture_emails_by_month, linewidth='1.6', color='#6D676E', alpha=0.92, label='Culture')
# plt.plot(months, dp_misc_emails_by_month, linewidth='2', color='black', alpha=0.73, label='Misc.')
plt.plot(months, dp_preprofessional_emails_by_month, linewidth='1.6', color='#099B76', alpha=0.92, label='Political')
plt.plot(months, dp_political_emails_by_month, linewidth='1.6', color='#F1D96F', alpha=0.92, label='Preprofessional')
plt.plot(months, dp_service_emails_by_month, linewidth='1.6', color='#9948C1', alpha=0.92, label='Service')
# titling and axis labeling
plt.ylabel("No. of Emails Sent", fontsize=16, **csfont)
plt.title("Email Topics Over Time", fontsize=18, **csfont)
# fill in legend
plt.legend(prop = {"family": 'cmr10' }, loc ="best")
# customize tick display
plt.xticks(months, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)
# save figure
plt.savefig('../analysis/email_topics/plots/dp_email_topic_counts_' + str(start_year) + '-' + str(end_year) +'.png', dpi=300, bbox_inches="tight")
# clear figure
fig.clf()

# creating the next chart
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
# plot
plt.plot(months, normalized_dp_arts_emails_by_month, linewidth='2', color='#96031A', alpha=0.73, label='Arts')
plt.plot(months, normalized_dp_athletics_emails_by_month, linewidth='2', color='#16041F', alpha=0.73, label='Athletics')
plt.plot(months, normalized_dp_culture_emails_by_month, linewidth='2', color='#6D676E', alpha=0.73, label='Culture')
# plt.plot(months, normalized_dp_misc_emails_by_month, linewidth='2', color='black', alpha=0.73, label='Misc.')
plt.plot(months, normalized_dp_preprofessional_emails_by_month, linewidth='2', color='#099B76', alpha=0.73, label='Political')
plt.plot(months, normalized_dp_political_emails_by_month, linewidth='2', color='#F1D96F', alpha=0.73, label='Preprofessional')
plt.plot(months, normalized_dp_service_emails_by_month, linewidth='2', color='#9948C1', alpha=0.73, label='Service')
# titling and axis labeling
plt.ylabel("No. of Emails Sent", fontsize=16, **csfont)
plt.title("Email Topics Over Time Normalized by No. Active Users", fontsize=18, **csfont)
# fill in legend
plt.legend(prop = {"family": 'cmr10' }, loc ="best")
# customize tick display
plt.xticks(months, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)
# save figure
plt.savefig('../analysis/email_topics/plots/normalized_dp_email_topic_counts_' + str(start_year) + '-' + str(end_year) +'.png', dpi=300, bbox_inches="tight")
# clear figure
fig.clf()


"""
Color palette:
color='#96031A'
color='#16041F'
color='#6D676E'
color='#099B76'
color='#F1D96F'
color='#9948C1'
"""
