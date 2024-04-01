"""
Plotting script for varying epsilon size vs. private release accuracy,
on a query function with global sensitvity of 1.
"""
import pandas as pd
from opendp.mod import enable_features
enable_features("contrib")
import matplotlib.pyplot as plt
import numpy as np
from opendp.accuracy import laplacian_scale_to_accuracy
import sys
sys.path.append('../')
from opendp_helpers import *


# read in csv
printed_columns = ['email', 'affiliation', 'num_emails_sent']
df = pd.read_csv("../dataframes/sent_received_length_df.csv", usecols=printed_columns)
# each person can only contribute one row
max_contributions = 1
# define metadata according to df structure
metadata = {"column_names": ['index'] + list(df.columns)}
# create column transformation
col_trans = create_col_trans('num_emails_sent', str, metadata)
# redefine counting measurement to take in scale as an argument
def make_count_meas(scale):
    return (
        col_trans >>
        then_count() >>
        then_laplace(scale=scale)
    )

# study scales between 0.5 and 4
scales = np.linspace(0.5, 4., num=100)
# use a privacy mapping to determine the corresponding epsilon for each scale (counting query has sensitivity of 1)
epsilons = [make_count_meas(s).map(max_contributions) for s in scales]
# use built-in function to calculate the accuracy for a given scale on the counting query
accuracies = [laplacian_scale_to_accuracy(scale=s, alpha=0.05) for s in scales]


csfont = {'fontname':'cmr10'}
plt.rcParams.update({'font.size': 22})
# plot
fig = plt.figure(figsize = (10, 5))
plt.style.use('ggplot')
plt.plot(epsilons, accuracies, linewidth='3', color='maroon', alpha=0.73)
plt.title("Epsilon vs. Accuracy at a 95% Confidence Interval", fontsize=18, **csfont)
plt.xlabel("epsilon", fontsize=16, **csfont)
plt.ylabel("accuracy", fontsize=16, **csfont)

plt.savefig('../analysis/plots/epsilon_vs_accuracy.png', dpi=300, bbox_inches="tight")
