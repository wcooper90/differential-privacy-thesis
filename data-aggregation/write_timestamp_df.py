"""
Script to aggregate and write an individually-indexed dataframe to disk,
only containing metadata about individuals' timestamps about first and last emails
sent.
"""
import pandas as pd
from csv_aggregation import create_individual_db_dict
df_name = 'timestamp_df'
columns = ['email', 'first_sent_email_timestamp', 'last_sent_email_timestamp', 'avg_sent_email_timestamp']
df_columns = columns

# makes the written df smaller
remove_metadata = True
if not remove_metadata:
    columns += ['club_affiliations']

# aggregate and write
batch_nums = [i for i in range(1)]
d = create_individual_db_dict(batch_nums, columns=df_columns, list_count_limit=10, remove_metadata=remove_metadata)
df = pd.DataFrame.from_dict(d, orient='index', columns=columns)
df = df.reset_index(drop=True)
df.to_csv('dataframes/' + df_name + '.csv')
