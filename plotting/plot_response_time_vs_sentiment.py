"""
Plotting script for response time vs. parent email compound sentiment.
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
with open('../analysis/response_time_sentiment/dp_response_time_sentiment.txt') as f:
    data = f.read()
# load string as dictionary
js = json.loads(data)
# convert to dataframe
df = pd.DataFrame(js.items())
# appropriatly rename columns
df = df.rename(columns={0: 'time_bin', 1: 'avg_compound_parent_sentiment'})

# x and y lists
# time_bins = df['time_bin']
time_bins = ['0-4 hours', '4-8 hours', '8-24 hours', '24-72 hours', 'more than 72 hours']
avg_compound_parent_sentiment = df['avg_compound_parent_sentiment']

# creating the bar plot
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
plt.bar(time_bins, avg_compound_parent_sentiment, color ='maroon',
        width = 0.4, alpha=0.78)
plt.xlabel("Response Time", fontsize=16, **csfont)
plt.ylabel("Avg. Compound Sentiment of Parent Email", fontsize=16, **csfont)
plt.title("Average Sentiment of Parent Email by Response Time", fontsize=18, **csfont)
plt.xticks(rotation=32, ha='right', fontsize=14, **csfont)

# save figure
plt.savefig('../analysis/plots/avg_sentiment_by_response_time.png', dpi=300, bbox_inches="tight")
