"""
Script to aggregate and write an individually-indexed dataframe to disk,
only containing metadata about email content length
"""
import pandas as pd
from csv_aggregation import create_individual_db_dict

df_name = 'sent_received_length_df'
columns = ['email', 'affiliation', 'num_emails_sent', 'num_emails_received', 'avg_sent_content_length']
df_columns = columns

# makes the written df smaller
remove_metadata = True
if not remove_metadata:
    columns += ['club_affiliations']

# aggregate and write
batch_nums = [i for i in range(18)]
d = create_individual_db_dict(batch_nums, columns=df_columns, list_count_limit=float('inf'), remove_metadata=remove_metadata)
df = pd.DataFrame.from_dict(d, orient='index', columns=columns)
df = df.reset_index(drop=True)
df.to_csv('dataframes/' + df_name + '.csv')
