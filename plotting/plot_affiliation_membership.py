"""
Plotting script for dp count of users by affiliation (email domain).
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager


csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})

data = None
# reading the data from the file
with open('../analysis/affiliation_counts/dp_count_by_affiliation.txt') as f:
    data = f.read()
# load string as dictionary
js = json.loads(data)
# convert to dataframe
df = pd.DataFrame(js.items())
# appropriatly rename columns
df = df.rename(columns={0: 'affiliation', 1: 'num_emails'})
# sort values for bar chart, cutoff at 10 entries
df = df.sort_values('num_emails', ascending=False)[:10]

# x and y lists
affiliations = df['affiliation']
num_emails = df['num_emails']

# creating the bar plot
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
plt.bar(affiliations, num_emails, color ='maroon',
        width = 0.4, alpha=0.78)
plt.ylabel("No. of Domain Email Address", fontsize=16, **csfont)
plt.title("HCS Listserv Membership by Email Domain", fontsize=18, **csfont)
plt.xticks(rotation=32, ha='right', fontsize=14, **csfont)

# save figure
plt.savefig('../analysis/plots/membership_by_domain.png', dpi=300, bbox_inches="tight")
