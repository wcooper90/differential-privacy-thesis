"""
Plotting script for dp avg content length by Harvard affiliation
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager


csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})

dp_avg_length = None
# reading the data from the file
with open('../analysis/avg_content_length_by_harvard_affiliation/dp_avg_content_length_by_harvard_affiliation.txt') as f:
    dp_avg_length = f.read()
f.close()

js_dp_avg_length = json.loads(dp_avg_length)
df_dp_avg_length = pd.DataFrame(js_dp_avg_length.items())
df_dp_avg_length = df_dp_avg_length.rename(columns={0: 'affiliation', 1: 'dp-avg-content-length'})
df = df_dp_avg_length
affiliations = list(df.index.values.tolist())
x = np.arange(14)
dp_avg_content_length = df['dp-avg-content-length']

# creating the bar plot
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
width = 0.40
# plot data in grouped manner of bar type
plt.bar(x, dp_avg_content_length, width, label='DP')
plt.xlabel("Harvard Affiliation", fontsize=16, **csfont)
plt.ylabel("Length (in Characters)", fontsize=16, **csfont)
plt.title("Average Length of Sent Emails by Harvard Affiliation", fontsize=18, **csfont)
plt.legend(loc='best', prop = {"family": 'cmr10' })
xtick_labels = affiliations
xtick_labels = [xtick.upper() for xtick in xtick_labels]
plt.xticks(x, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)

# save figure
plt.savefig('../analysis/plots/avg_sent_content_length_by_harvard_affiliation.png', dpi=300, bbox_inches="tight")
