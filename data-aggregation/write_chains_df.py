"""
Write a dataframe with only the necessary columns for email thread analysis
to disk.
"""
import pandas as pd
import math
import numpy as np
from dateutil import parser
from tqdm import tqdm
from csv_aggregation import full_email_df


# function to collect the email ids of emails which belong to a thread
def collect_chain_ids(df):
    chain_email_ids = set([])
    for i, row in tqdm(df.iterrows()):
        # if the parent column is not nan, add both this email id and its parent email id
        if not isinstance(row['parent'], float):
            chain_email_ids.add(row['parent'])
            chain_email_ids.add(row['id'])
    return list(chain_email_ids)


# remove emails from the df that are not part of a chain
def remove_non_chain_emails(df, chain_email_ids):
    df = df[df['id'].isin(chain_email_ids)]
    return df


# add a column to denote response time between emails
# categorical variable
def add_response_time_column(df):

    # add new columns of nan values
    df["response-time"] = np.nan
    df['parent-sub-neg'] = np.nan
    df['parent-sub-neu'] = np.nan
    df['parent-sub-pos'] = np.nan
    df['parent-sub-com'] = np.nan
    df['parent-con-neg'] = np.nan
    df['parent-con-neu'] = np.nan
    df['parent-con-pos'] = np.nan
    df['parent-con-com'] = np.nan

    for i, row in tqdm(df.iterrows()):
        if not isinstance(row['parent'], float):
            parent_email = df.loc[df['id'] == row['parent']]
            if parent_email.empty:
                print("couldn't find parent email for id: {row}".format(row=row['id']))
                continue

            # get sentiments of parent email
            df.loc[i, 'parent-sub-neg'] = parent_email['sub-neg'].values[0]
            df.loc[i, 'parent-sub-neu'] = parent_email['sub-neu'].values[0]
            df.loc[i, 'parent-sub-pos'] = parent_email['sub-pos'].values[0]
            df.loc[i, 'parent-sub-com'] = parent_email['sub-com'].values[0]
            df.loc[i, 'parent-con-neg'] = parent_email['con-neg'].values[0]
            df.loc[i, 'parent-con-neu'] = parent_email['con-neu'].values[0]
            df.loc[i, 'parent-con-pos'] = parent_email['con-pos'].values[0]
            df.loc[i, 'parent-con-com'] = parent_email['con-com'].values[0]

            row_timestamp = parser.parse(row['timestamp'])
            parent_timestamp = parser.parse(parent_email['timestamp'].values[0])
            timedelta = row_timestamp - parent_timestamp
            hours = timedelta.days * 24 + timedelta.seconds // 3600

            # response time categories, created by # of hours
            response_time_category = None
            if hours < 4:
                response_time_category = 1
            elif hours < 8:
                response_time_category = 2
            elif hours < 24:
                response_time_category = 3
            elif hours < 72:
                response_time_category = 4
            elif hours < 168:
                response_time_category = 5
            else:
                response_time_category = 6

            df.loc[i, 'response-time'] = response_time_category

    return df


# columns of interest
columns = ['id',  # email id
            'parent', # email's parent chain id, if applicable
            'to',  # receiving email
            'from', # sender email
            'timestamp', # timestamp
            'affiliation', # club affiliation, if either sender or receiver is a club email
            'to-affiliation', # email domain of receiver
            'from-affiliation', # email domain of sender
            'sub-neg', # negative sentiment in subject
            'sub-neu', # neutral sentiment in subject
            'sub-pos', # positive sentiment in subject
            'sub-com', # compound sentiment in subject
            'con-neg', # negative sentiment in content
            'con-neu', # neutral sentiment in content
            'con-pos', # positive sentiment in content
            'con-com', # compound sentiment in content
            'topic', # email topic
            ]


# sample the email csv batches
# randomly selected dataframes 6, 9, and 12
batch_nums = [6, 9, 12]
email_count_limit = float("inf")
email_df = full_email_df(batch_nums, columns, email_count_limit=email_count_limit)
chain_email_ids = collect_chain_ids(email_df)
email_df = remove_non_chain_emails(email_df, chain_email_ids)
email_df = add_response_time_column(email_df)
df_name = 'response_time_df'
email_df.to_csv('./dataframes/' + df_name + '.csv')
