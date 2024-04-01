"""
Script to aggregate and write the full individually-indexed dataframe to disk,
including sentiments and topics
"""
import pandas as pd
from csv_aggregation import create_individual_db_from_email_dfs

df_name = 'full_individual_df'
# columns of interest
email_column_names = ['id',  # email id
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
                    'topic' # categorized topic
                    ]
individual_column_names = ['email',
                            'affiliation',
                            'avg-content-length',
                            'first-email-timestamp',
                            'last-email-timestamp',
                            'avg-received-sub-neg',
                            "avg-received-sub-neu",
                            "avg-received-sub-pos",
                            "avg-received-sub-com",
                            "avg-sent-sub-neg",
                            "avg-sent-sub-neu",
                            "avg-sent-sub-pos",
                            "avg-sent-sub-com",
                            "avg-received-con-neg",
                            "avg-received-con-neu",
                            "avg-received-con-pos",
                            "avg-received-con-com",
                            "avg-sent-con-neg",
                            "avg-sent-con-neu",
                            "avg-sent-con-pos",
                            "avg-sent-con-com",
                            "sum-sent-con-semitic-wf",
                            "sum-sent-con-crypto-wf",
                            "sum-sent-sub-semitic-wf",
                            "sum-sent-sub-crypto-wf",
                            "num-club-affiliations",
                            "num-emails-sent",
                            "num-emails-received",
                            "num-sent-arts",
                            "num-sent-athletics",
                            "num-sent-culture",
                            "num-sent-politics",
                            "num-sent-preprofessional",
                            "num-sent-service",
                            "num-sent-misc",
                            "num-received-arts",
                            "num-received-athletics",
                            "num-received-culture",
                            "num-received-politics",
                            "num-received-preprofessional",
                            "num-received-service",
                            "num-received-misc"
                            ]

batch_nums = [i for i in range(18)]
full_ind_df = create_individual_db_from_email_dfs(batch_nums, email_column_names, individual_column_names)
full_ind_df.to_csv('./dataframes/' + df_name + '.csv')
