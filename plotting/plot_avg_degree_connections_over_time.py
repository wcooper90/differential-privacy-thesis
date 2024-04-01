"""
Plotting script for average subgraph connectivity over time.
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})
connections_data = None
# reading the data from the file
with open('../../analysis/avg_degree_connections/connections_over_time.txt') as f:
    connections_data = f.read()

# load string as dictionary
js = json.loads(connections_data)
dp_fas_fas_connections = js['fas-fas']
dp_fas_college_connections = js['fas-college']
dp_fas_gmail_connections = js['fas-gmail']
dp_college_college_connections = js['college-college']
dp_college_gmail_connections = js['college-gmail']
dp_gmail_gmail_connections = js['gmail-gmail']


x_axis = np.arange(len(dp_fas_fas_connections))
# creating the chart
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
# plot
plt.bar(x_axis - 0.25, dp_fas_fas_connections, 0.1, color='maroon', alpha=0.73, label="fas-fas")
plt.bar(x_axis - 0.15, dp_fas_college_connections, 0.1, color='#16041F', alpha=0.73, label="fas-college")
plt.bar(x_axis - 0.05, dp_fas_gmail_connections, 0.1, color='#099B76', alpha=0.73, label="fas-gmail")
plt.bar(x_axis + 0.05, dp_college_college_connections, 0.1, color='#9948C1', alpha=0.73, label="college-college")
plt.bar(x_axis + 0.15, dp_college_gmail_connections, 0.1, color='#6D676E', alpha=0.73, label="college-gmail")
plt.bar(x_axis + 0.25, dp_gmail_gmail_connections, 0.1, color='#277DAF', alpha=0.73, label="gmail-gmail")

# plt.ylabel("No. of Active Email Addresses", fontsize=16, **csfont)
plt.title("Average No. of Connections Between Domains Over Time", fontsize=18, **csfont)

# fill in legend
plt.legend(prop = {"family": 'cmr10' }, loc ="best")

# create custom xtick labels
xtick_labels = ['2000-2003', '2004-2007', '2008-2011', '2012-2015', '2016-2019', '2020-2023']

# customize tick display
plt.xticks(x_axis, xtick_labels, rotation=32, ha='right', fontsize=13, **csfont)
plt.yticks(fontsize=12, **csfont)

# save figure
plt.savefig('../../analysis/plots/dp_avg_connections_over_time2.png', dpi=300, bbox_inches="tight")


"""
Color palette:
color='#96031A'
color='#16041F'
color='#6D676E'
color='#099B76'
color='#F1D96F'
color='#9948C1'
"""
