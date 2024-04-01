"""
Plotting script for total number of sent emails by email affiliation (domain)
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
with open('../analysis/affiliation_sum_emails_sent/dp_sum_sent_by_affiliation.txt') as f:
    data = f.read()
# load string as dictionary
js = json.loads(data)
# convert to dataframe
df = pd.DataFrame(js.items())
# appropriatly rename columns
df = df.rename(columns={0: 'affiliation', 1: 'num_emails_sent'})
# sort values for bar chart, cutoff at 10 entries
df = df.sort_values('num_emails_sent', ascending=False)[:10]

# x and y lists
affiliations = df['affiliation']
num_emails_sent = df['num_emails_sent']

# creating the bar plot
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
plt.bar(affiliations, num_emails_sent, color ='maroon',
        width = 0.4, alpha=0.78)
plt.ylabel("Sum of Emails Sent", fontsize=16, **csfont)
plt.title("Total Number of Emails Sent by Sender Domain", fontsize=18, **csfont)
plt.xticks(rotation=32, ha='right', fontsize=14, **csfont)

# save figure
plt.savefig('../analysis/plots/sum_sent_by_domain.png', dpi=300, bbox_inches="tight")
