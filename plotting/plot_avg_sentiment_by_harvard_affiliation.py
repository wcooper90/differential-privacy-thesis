"""
Plotting script for dp avg compound sentiment of sent emails by Harvard affiliation.
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager


csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})
dp_com = None
dp_neg = None
dp_neu = None
dp_pos = None


# reading the data from the file
with open('../analysis/sentiment_by_harvard_affiliation/dp_compound_sentiment_by_harvard_affiliation.txt') as f:
    dp_com = f.read()
f.close()
with open('../analysis/sentiment_by_harvard_affiliation/dp_negative_sentiment_by_harvard_affiliation.txt') as f:
    dp_neg = f.read()
f.close()
with open('../analysis/sentiment_by_harvard_affiliation/dp_neutral_sentiment_by_harvard_affiliation.txt') as f:
    dp_neu = f.read()
f.close()
with open('../analysis/sentiment_by_harvard_affiliation/dp_positive_sentiment_by_harvard_affiliation.txt') as f:
    dp_pos = f.read()
f.close()

# load sentiment index data from disk
js_dp_com = json.loads(dp_com)
js_dp_neg = json.loads(dp_neg)
js_dp_neu = json.loads(dp_neu)
js_dp_pos = json.loads(dp_pos)
df_dp_com = pd.DataFrame(js_dp_com.items())
df_dp_com = df_dp_com.rename(columns={0: 'affiliation', 1: 'dp-com'})
df_dp_neg = pd.DataFrame(js_dp_neg.items())
df_dp_neg = df_dp_neg.rename(columns={0: 'affiliation', 1: 'dp-neg'})
df_dp_neu = pd.DataFrame(js_dp_neu.items())
df_dp_neu = df_dp_neu.rename(columns={0: 'affiliation', 1: 'dp-neu'})
df_dp_pos = pd.DataFrame(js_dp_pos.items())
df_dp_pos = df_dp_pos.rename(columns={0: 'affiliation', 1: 'dp-pos'})

# concatenate dataframes
df = pd.concat([df_dp_com.set_index('affiliation'),df_dp_neg.set_index('affiliation')], axis=1, join='inner')
df = pd.concat([df, df_dp_neu.set_index('affiliation')], axis=1, join='inner')
df = pd.concat([df, df_dp_pos.set_index('affiliation')], axis=1, join='inner')

affiliations = list(df.index.values.tolist())
x = np.arange(14)
dp_compound_sentiments = df['dp-com']
dp_negative_sentiments = df['dp-neg']
dp_neutral_sentiments = df['dp-neu']
dp_positive_sentiments = df['dp-pos']

# creating the bar plot
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')

width = 0.20

# plot data in grouped manner of bar type
plt.bar(x-0.3, dp_compound_sentiments, width, label='Compound')
plt.bar(x-0.1, dp_positive_sentiments, width, label='Positive')
plt.bar(x+0.1, dp_neutral_sentiments, width, label='Neutral')
plt.bar(x+0.3, dp_negative_sentiments, width, label='Negative')

plt.xlabel("Email Domain", fontsize=16, **csfont)
plt.ylabel("Sentiment Index", fontsize=16, **csfont)
plt.title("Average Sentiment of Sent Emails by Harvard Domain", fontsize=18, **csfont)
plt.legend(loc='best', prop = {"family": 'cmr10' })

xtick_labels = affiliations
xtick_labels = [xtick.upper() for xtick in xtick_labels]
plt.xticks(x, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)

# save figure
plt.savefig('../analysis/plots/avg_sent_sentiment_by_harvard_affiliation.png', dpi=300, bbox_inches="tight")
