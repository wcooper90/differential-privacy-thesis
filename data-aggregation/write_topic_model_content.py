"""
Script to write the dp topic model's results on each email, saves dataframe to disk
"""
import pandas as pd
import numpy as np
import time
import sys
from csv_aggregation import create_topic_model_df

# columns to write
column_names = ['id',  # email id
                'topic_num', # the topic's value
                ]

final_df = pd.DataFrame(columns=column_names)
# use batch processing
for i in range(0, 18):
    s = time.time()
    batch_nums = [i]
    # use helper function to create full dataframe
    df = create_topic_model_df(batch_nums, column_names, list_count_limit=float('inf'), parent_dir=True)
    # reset index and print
    df = df.reset_index(drop=True)
    final_df = pd.concat([final_df, df])
    e = time.time()
    t = e - s
    print("Processing batch " + str(i) + " took " + str(round(t, 4)) + " seconds.")

# name of csv file to save to
df_name = 'full_email_tm_df'
final_df.to_csv('../dataframes/' + df_name + '.csv')
