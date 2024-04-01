"""
Script to aggregate and write an initial individually-indexed dataframe to disk
"""
import pandas as pd
from csv_aggregation import create_individual_db_dict


df_name = 'full_df'
columns = ['email', 'affiliation', 'num_emails_sent', 'num_emails_received',
            'num_club_affiliations', 'avg_sent_sentiment',
            'avg_received_sentiment', 'avg_sent_content_length', 'timestamps']

# makes the written df smaller
remove_metadata = True
if not remove_metadata:
    columns += ['club_affiliations']

# aggregate and write
batch_nums = [i for i in range(18)]
d = create_individual_db_dict(batch_nums, columns=df_columns, list_count_limit=10, remove_metadata=remove_metadata)
df = pd.DataFrame.from_dict(d, orient='index', columns=columns)
df = df.reset_index(drop=True)
df.to_csv('dataframes/' + df_name + '.csv')
