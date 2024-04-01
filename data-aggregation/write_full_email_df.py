"""
Script to aggregate raw emails from each of the 18 batches into
metadata dataframes
"""
import pandas as pd
from csv_aggregation import create_email_pd


# columns of interest
column_names = ['id',  # email id
                'parent', # email's parent chain id, if applicable
                'to',  # receiving email
                'from', # sender email
                'timestamp', # timestamp
                'affiliation', # club affiliation, if either sender or receiver is a club email
                'to-affiliation', # email domain of receiver
                'from-affiliation', # email domain of sender
                'content-length', # length (in characters) of content
                'sub-neg', # negative sentiment in subject
                'sub-neu', # neutral sentiment in subject
                'sub-pos', # positive sentiment in subject
                'sub-com', # compound sentiment in subject
                'con-neg', # negative sentiment in content
                'con-neu', # neutral sentiment in content
                'con-pos', # positive sentiment in content
                'con-com', # compound sentiment in content
                'con-semitic-wf', # number of semitic related stopwords in content
                'con-crypto-wf', # number of crypto related stopwords in content
                'sub-semitic-wf', # number of semitic related stopwords in subject
                'sub-crypto-wf', # number of crypto related stopwords in subject
                'con-felipes-wf', # number of semitic related stopwords in content
                'con-jefes-wf', # number of crypto related stopwords in content
                'sub-felipes-wf', # number of semitic related stopwords in subject
                'sub-jefes-wf', # number of crypto related stopwords in subject
                'topic' # calculated topic
                ]

# define a list of content topics for the parser to count relevant stopwords
content_topics = ['semitism', 'crypto', 'felipes', 'jefes']

# to print head
printed_columns = ['id', 'content-length', 'affiliation']


# use batch processing
for i in range(14, 18):
    # name of csv file to save to
    df_name = 'batch' + str(i) + '_email_df'
    batch_nums = [i]
    # use helper function to create full dataframe
    df = create_email_pd(batch_nums, column_names, content_topics, list_count_limit=float('inf'), parent_dir=False)
    # reset index and print
    df = df.reset_index(drop=True)
    df.to_csv('./dataframes/' + df_name + '.csv')
