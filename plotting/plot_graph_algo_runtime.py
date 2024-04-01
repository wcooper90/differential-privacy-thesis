"""
Plotting script for graph-dp algorithm runtimes
"""
import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager


csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})
runtime_data = None
# reading the data from the file
with open('../../analysis/graph_dp_algo_runtime/dp_graph_algos_runtimes.txt') as f:
    runtime_data = f.read()

# load string as dictionary
js = json.loads(runtime_data)
max_flow_edge_count_times = js['max-flow-edge-count']
opt_based_edge_count_times = js['opt-based-edge-count']
opt_based_kstar_count_times = js['opt-based-kstar-count']


x_axis = np.arange(len(max_flow_edge_count_times))
# creating the chart
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
# plot
plt.bar(x_axis - 0.2, max_flow_edge_count_times, 0.2, color='maroon', alpha=0.73, label="max-flow-edge-count")
plt.bar(x_axis, opt_based_edge_count_times, 0.2, color='#16041F', alpha=0.73, label="optimization-based-edge-count")
plt.bar(x_axis + 0.2, opt_based_kstar_count_times, 0.2, color='#099B76', alpha=0.73, label="optimization-based-kstar-count")

plt.ylabel("Runtime (log(seconds))", fontsize=16, **csfont)
plt.yscale("log")
plt.title("Runtime of DP-Graph Algorithms by Graph Size", fontsize=18, **csfont)

# fill in legend
plt.legend(prop = {"family": 'cmr10' }, loc ="best")

# create custom xtick labels
xtick_labels = ['n=32', 'n=64', 'n=128', 'n=256', 'n=512']

# customize tick display
plt.xticks(x_axis, xtick_labels, rotation=32, ha='right', fontsize=10, **csfont)
plt.yticks(fontsize=10, **csfont)

# save figure
plt.savefig('../../analysis/plots/graph_dp_runtime.png', dpi=300, bbox_inches="tight")
