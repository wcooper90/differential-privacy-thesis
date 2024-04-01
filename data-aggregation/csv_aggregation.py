"""
Functions to process raw scp'd email data into email-indexed and
individual-indexed dataframes
"""
import pandas as pd
import numpy as np
import os
import sys
from tqdm import tqdm
from helpers import *


# create a dataframe for topic modeling
def create_topic_model_df(batch_nums, column_names, list_count_limit=float('inf'), parent_dir=False):
    final_df = pd.DataFrame(columns=column_names)
    extractor = Extractor(column_names)
    list_counter = 0

    # for each batch number provided
    for batch_num in batch_nums:
        paths = []
        list_dirs = []
        scp_path = ""
        # when running from 'complete-scripts' folder
        if parent_dir:
            scp_path = '../scp-results/batch' + str(batch_num) + '/'
        # when running from main folder
        else:
            scp_path = './scp-results/batch' + str(batch_num) + '/'

        # find individual list directories
        for subdir, dirs, files in os.walk(scp_path):
            for dir in dirs:
                list_dirs.append(dir)

        # for each list directory
        for list_dir in tqdm(list_dirs):
            # find the files
            file_list = os.listdir(scp_path + list_dir)
            # for each file, pull out csv
            for file in file_list:
                df = pd.read_csv(scp_path + list_dir + '/' + file)
                df = process_emails_for_topic_models(df, extractor, column_names)
                final_df = pd.concat([final_df, df])

            list_counter += 1
            # break if there's a limit
            if list_counter > list_count_limit:
                break

        # break if there's a limit
        if list_counter > list_count_limit:
            break

    return final_df


# process each email for topic modeling dataframe
def process_emails_for_topic_models(df, extractor, column_names):
    new_df = pd.DataFrame(columns=column_names)
    for i, row in df.iterrows():
        d = extractor.get_email_info(row, topic_model=True)
        new_row = [d[col] for col in column_names]
        # accidental empty first row was appended to some of the scp'd files, so hardcoded to ignore
        # if new_row[4] is None and new_row[2] == -1 and new_row[3] == -1:
        #     continue
        new_df.loc[len(new_df.index)] = new_row
    return new_df


# concatenate and return a dataframe with all raw email data
def full_email_df(batch_nums, email_columns, parent_dir=False, email_count_limit=float('inf')):
    email_df = pd.DataFrame(columns=email_columns)

    # for each batch number provided
    for batch_num in tqdm(batch_nums):
        path = None
        # when running from 'complete-scripts' folder
        if parent_dir:
            path = '../dataframes/batch' + str(batch_num) + '_email_df.csv'
        # when running from main folder
        else:
            path = './dataframes/batch' + str(batch_num) + '_email_df.csv'

        df = None
        # hardcoded threshold because no batch of mailing lists has more than a million emails
        if email_count_limit < 1000000:
            df = pd.read_csv(path, usecols=email_columns, nrows=email_count_limit)
        else:
            df = pd.read_csv(path, usecols=email_columns)

        # concatenate into final dataframe
        email_df = pd.concat([email_df, df])

    return email_df


# aggregate email information to form individually-indexed dataframe
def create_individual_db_from_email_dfs(batch_nums, email_columns, individual_columns, parent_dir=False):
    # construct full raw email dataframe
    email_df = full_email_df(batch_nums, email_columns, parent_dir)
    # aggregate by individual email address
    individual_dict = index_by_individual(email_df, individual_columns)
    # create final dataframe
    final_df = pd.DataFrame.from_dict(individual_dict, orient='index', columns=individual_columns)
    final_df = final_df.reset_index(drop=True)
    return final_df


# individual aggregation
def index_by_individual(df, individual_columns):
    reversed_topic_mapping = {0: 'arts', 1: 'athletics', 2: 'culture', 3: 'misc',
                            4: 'politics', 5: 'preprofessional', 6: 'service'}
    d = {}
    for i, row in tqdm(df.iterrows()):
        to_dict = {}
        from_dict = {}
        # initialize to and from dictionaries
        if row['to'] in d:
            to_dict = d[row['to']]
        else:
            to_dict = initialize_person_entry(row['to'], row['to-affiliation'], from_preprocessed=True)
        if row['from'] in d:
            from_dict = d[row['from']]
        else:
            from_dict = initialize_person_entry(row['from'], row['from-affiliation'], from_preprocessed=True)

        # update number of emails sent and received
        to_dict['num-emails-received'] += 1
        from_dict['num-emails-sent'] += 1

        # update first and last email timestamps
        if from_dict['first-email-timestamp'] is None and from_dict['last-email-timestamp'] is None:
            from_dict['first-email-timestamp'] = row['timestamp']
            from_dict['last-email-timestamp'] = row['timestamp']
        else:
            try:
                if row['timestamp'] > from_dict['last-email-timestamp']:
                    from_dict['last-email-timestamp'] = row['timestamp']
                elif row['timestamp'] < from_dict['first-email-timestamp']:
                    from_dict['first-email-timestamp'] = row['timestamp']
            except Exception as E:
                print("encountered nan value in timestamp")

        # accumulate emails sent by topic
        topic = reversed_topic_mapping[row['topic']]
        receiver_topic_key = 'num-received-' + topic
        sender_topic_key = 'num-sent-' + topic
        to_dict[receiver_topic_key] += 1
        from_dict[sender_topic_key] += 1

        # accumulate sum of sentiments for receiver
        to_dict['avg-received-sub-neg'] += row['sub-neg']
        to_dict['avg-received-sub-neu'] += row['sub-neu']
        to_dict['avg-received-sub-pos'] += row['sub-pos']
        to_dict['avg-received-sub-com'] += row['sub-com']

        to_dict['avg-received-con-neg'] += row['con-neg']
        to_dict['avg-received-con-neu'] += row['con-neu']
        to_dict['avg-received-con-pos'] += row['con-pos']
        to_dict['avg-received-con-com'] += row['con-com']

        # accumulate sum of sentiments for sender
        from_dict['avg-sent-sub-neg'] += row['sub-neg']
        from_dict['avg-sent-sub-neu'] += row['sub-neu']
        from_dict['avg-sent-sub-pos'] += row['sub-pos']
        from_dict['avg-sent-sub-com'] += row['sub-com']

        from_dict['avg-sent-con-neg'] += row['con-neg']
        from_dict['avg-sent-con-neu'] += row['con-neu']
        from_dict['avg-sent-con-pos'] += row['con-pos']
        from_dict['avg-sent-con-com'] += row['con-com']


        # update word frequencies (leaving out jefes and felipes stopwords)
        from_dict['sum-sent-sub-semitic-wf'] += row['sub-semitic-wf']
        from_dict['sum-sent-sub-crypto-wf'] += row['sub-crypto-wf']
        from_dict['sum-sent-con-semitic-wf'] += row['con-semitic-wf']
        from_dict['sum-sent-con-crypto-wf'] += row['con-crypto-wf']

        # accumulate sum of sent content length
        from_dict['avg-content-length'] += row['content-length']

        # update affiliations
        if row['affiliation'] not in to_dict['num-club-affiliations']:
            to_dict['num-club-affiliations'].add(row['affiliation'])
        if row['affiliation'] not in from_dict['num-club-affiliations']:
            from_dict['num-club-affiliations'].add(row['affiliation'])

        # update global dictionary d
        d[row['to']] = to_dict
        d[row['from']] = from_dict


    # post-processing to calculate averages and sums
    for key in d.keys():
        # number of affiliations
        d[key]['num-club-affiliations'] = len(d[key]['num-club-affiliations'])

        # averages of received sentiments
        if d[key]['num-emails-received'] > 0:
            d[key]['avg-received-sub-neg'] = round(d[key]['avg-received-sub-neg'] / d[key]['num-emails-received'], 4)
            d[key]['avg-received-sub-neu'] = round(d[key]['avg-received-sub-neu'] / d[key]['num-emails-received'], 4)
            d[key]['avg-received-sub-pos'] = round(d[key]['avg-received-sub-pos'] / d[key]['num-emails-received'], 4)
            d[key]['avg-received-sub-com'] = round(d[key]['avg-received-sub-com'] / d[key]['num-emails-received'], 4)

            d[key]['avg-received-con-neg'] = round(d[key]['avg-received-con-neg'] / d[key]['num-emails-received'], 4)
            d[key]['avg-received-con-neu'] = round(d[key]['avg-received-con-neu'] / d[key]['num-emails-received'], 4)
            d[key]['avg-received-con-pos'] = round(d[key]['avg-received-con-pos'] / d[key]['num-emails-received'], 4)
            d[key]['avg-received-con-com'] = round(d[key]['avg-received-con-com'] / d[key]['num-emails-received'], 4)

        # averages of sent sentiments and sent content length
        if d[key]['num-emails-sent'] > 0:
            d[key]['avg-sent-sub-neg'] = round(d[key]['avg-sent-sub-neg'] / d[key]['num-emails-sent'], 4)
            d[key]['avg-sent-sub-neu'] = round(d[key]['avg-sent-sub-neu'] / d[key]['num-emails-sent'], 4)
            d[key]['avg-sent-sub-pos'] = round(d[key]['avg-sent-sub-pos'] / d[key]['num-emails-sent'], 4)
            d[key]['avg-sent-sub-com'] = round(d[key]['avg-sent-sub-com'] / d[key]['num-emails-sent'], 4)


            d[key]['avg-sent-con-neg'] = round(d[key]['avg-sent-con-neg'] / d[key]['num-emails-sent'], 4)
            d[key]['avg-sent-con-neu'] = round(d[key]['avg-sent-con-neu'] / d[key]['num-emails-sent'], 4)
            d[key]['avg-sent-con-pos'] = round(d[key]['avg-sent-con-pos'] / d[key]['num-emails-sent'], 4)
            d[key]['avg-sent-con-com'] = round(d[key]['avg-sent-con-com'] / d[key]['num-emails-sent'], 4)

            d[key]['avg-content-length'] = round(d[key]['avg-content-length'] / d[key]['num-emails-sent'], 4)

    # return global dictionary
    return d


# initialize an entry in the individually-indexed dataframe
def initialize_person_entry(email, affiliation, from_preprocessed=False):
    if not from_preprocessed:
        return {"email": email, "affiliation": affiliation, "num_emails_sent": 0, "num_emails_received": 0,
                "num_club_affiliations": 0, "avg_sent_sentiment": {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0},
                "avg_received_sentiment": {'neg': 0.0, 'neu': 0.0, 'pos': 0.0, 'compound': 0.0},
                'avg_sent_content_length': 0, 'club_affiliations': set([])}

    else:
        return {"email": email, "affiliation": affiliation, "avg-content-length": 0, "first-email-timestamp":None,
                "last-email-timestamp": None, "avg-received-sub-neg": 0, "avg-received-sub-neu": 0, "avg-received-sub-pos": 0,
                "avg-received-sub-com": 0, "avg-sent-sub-neg": 0, "avg-sent-sub-neu": 0, "avg-sent-sub-pos": 0,
                "avg-sent-sub-com": 0, "avg-received-con-neg": 0, "avg-received-con-neu": 0, "avg-received-con-pos": 0,
                "avg-received-con-com": 0, "avg-sent-con-neg": 0, "avg-sent-con-neu": 0, "avg-sent-con-pos": 0,
                "avg-sent-con-com": 0, "sum-sent-con-semitic-wf": 0, "sum-sent-con-crypto-wf": 0,
                "sum-sent-sub-semitic-wf": 0, "sum-sent-sub-crypto-wf": 0, "num-club-affiliations": set([]),
                "num-emails-sent": 0, "num-emails-received": 0, "num-sent-arts": 0, "num-sent-athletics": 0,
                "num-sent-culture": 0, "num-sent-politics": 0, "num-sent-preprofessional": 0, "num-sent-service": 0,
                "num-sent-misc": 0, "num-received-arts": 0,  "num-received-athletics": 0, "num-received-culture": 0,
                "num-received-politics": 0, "num-received-preprofessional": 0, "num-received-service": 0, "num-received-misc": 0}


# create a processed email-indexed metadata dataframe
def create_email_pd(batch_nums, column_names, content_topics, list_count_limit=float('inf'), parent_dir=False):
    final_df = pd.DataFrame(columns=column_names)
    extractor = Extractor(column_names, content_topics)
    list_counter = 0

    # for each batch number provided
    for batch_num in batch_nums:
        paths = []
        list_dirs = []
        scp_path = ""
        # when running from 'complete-scripts' folder
        if parent_dir:
            scp_path = '../scp-results/batch' + str(batch_num) + '/'
        # when running from main folder
        else:
            scp_path = './scp-results/batch' + str(batch_num) + '/'

        # find individual list directories
        for subdir, dirs, files in os.walk(scp_path):
            for dir in dirs:
                list_dirs.append(dir)

        # for each list directory
        for list_dir in tqdm(list_dirs):
            # find the files
            file_list = os.listdir(scp_path + list_dir)
            # for each file, pull out csv
            for file in file_list:
                df = pd.read_csv(scp_path + list_dir + '/' + file)
                df = process_email_csv(df, extractor, column_names)
                final_df = pd.concat([final_df, df])

            list_counter += 1
            # break if there's a limit
            if list_counter > list_count_limit:
                break

        # break if there's a limit
        if list_counter > list_count_limit:
            break

    return final_df


# create a processed individually-indexed dataframe
def create_full_pd(batch_nums, column_names, list_count_limit=float('inf'), parent_dir=False):
    final_df = pd.DataFrame(columns=column_names)

    list_counter = 0

    # for each batch number provided
    for batch_num in batch_nums:
        paths = []
        list_dirs = []
        scp_path = ""
        # when running from 'complete-scripts' folder
        if parent_dir:
            scp_path = '../scp-results/batch' + str(batch_num) + '/'
        # when running from main folder
        else:
            scp_path = './scp-results/batch' + str(batch_num) + '/'

        # find individual list directories
        for subdir, dirs, files in os.walk(scp_path):
            for dir in dirs:
                list_dirs.append(dir)

        # for each list directory
        for list_dir in tqdm(list_dirs):
            # find the files
            file_list = os.listdir(scp_path + list_dir)
            # for each file, pull out csv
            for file in file_list:
                df = pd.read_csv(scp_path + list_dir + '/' + file, usecols=column_names)
                final_df = pd.concat([final_df, df])

            list_counter += 1
            # break if there's a limit
            if list_counter > list_count_limit:
                break

        # break if there's a limit
        if list_counter > list_count_limit:
            break

    return final_df


# aggregate information on individuals and return as a dictionary
def create_individual_db_dict(batch_nums, columns, list_count_limit=float('inf'), remove_metadata=True):

    d = {}
    list_counter = 0
    extractor = Extractor(columns)

    # for each batch number provided
    for batch_num in batch_nums:
        paths = []
        list_dirs = []
        scp_path = '/mnt/c/Users/wcoop/Desktop/Thesis/scp-results/batch' + str(batch_num) + '/'
        # find individual list directories
        for subdir, dirs, files in os.walk(scp_path):
            for dir in dirs:
                list_dirs.append(dir)

        # for each list directory
        for list_dir in tqdm(list_dirs):
            # find the files
            file_list = os.listdir(scp_path + list_dir)
            # for each file, pull out csv
            for file in file_list:

                file_path = scp_path + list_dir + '/' + file
                d = process_csv(d, file_path, extractor)

            list_counter += 1
            # break if there's a limit
            if list_counter > list_count_limit:
                break

        # break if there's a limit
        if list_counter > list_count_limit:
            break

    # remove large columns before writing
    if remove_metadata:
        # delete the set of club affiliations, only keep the number of affiliations
        for key in d:
            del d[key]['club_affiliations']

    return d


# process emails in a given batch dataframe
def process_email_csv(df, extractor, column_names):
    new_df = pd.DataFrame(columns=column_names)
    for i, row in df.iterrows():
        d = extractor.get_email_info(row)
        new_row = [d[col] for col in column_names]
        # accidental empty first row was appended to some of the scp'd files, so hardcoded to ignore
        if new_row[4] is None and new_row[2] == -1 and new_row[3] == -1:
            continue
        new_df.loc[len(new_df.index)] = new_row
    return new_df


# process emails from a given file path
def process_csv(d, file_path, extractor):
    df = pd.read_csv(file_path)
    for i, row in df.iterrows():
        # process the row
        extract = extractor.parse(row)
        # create dictionaries to update senders and receivers
        to_dict = {}
        from_dict = {}
        if extract['to'] in d:
            to_dict = d[extract['to']]
        else:
            to_dict = initialize_person_entry(extract['to'], extract['to-affiliation'])
        if extract['from'] in d:
            from_dict = d[extract['from']]
        else:
            from_dict = initialize_person_entry(extract['from'], extract['from-affiliation'])


        # increment num emails
        from_dict['num_emails_sent'] += 1
        to_dict['num_emails_received'] += 1

        # only do these calculations if they are needed in the specified df
        if 'num_club_affiliations' in extractor.columns:
            # increment num_club_affiliations
            if extract['club-affiliation'] and extract['club-affiliation'] not in to_dict['club_affiliations']:
                to_dict['club_affiliations'].add(extract['club-affiliation'])
                to_dict['num_club_affiliations'] += 1
            if extract['club-affiliation'] and extract['club-affiliation'] not in from_dict['club_affiliations']:
                from_dict['club_affiliations'].add(extract['club-affiliation'])
                from_dict['num_club_affiliations'] += 1

        # expand the inner sentiment dictionary to be plain columns in the final dictionary
        if 'avg_sent_sentiment' in extractor.columns or 'avg_received_sentiment' in extractor.columns:
            # update average sentiments on receiving end
            if extract['content-sentiment'] is not None:
                received_sentiments = to_dict['avg_received_sentiment']
                for key in received_sentiments:
                    received_sentiments[key] = round(((to_dict['num_emails_received'] - 1) * received_sentiments[key] + extract['content-sentiment'][key]) / to_dict['num_emails_received'], 4)
                to_dict['avg_received_sentiment'] = received_sentiments

                # update average sentiments on sending end
                sent_sentiments = from_dict['avg_sent_sentiment']
                for key in sent_sentiments:
                    sent_sentiments[key] = round(((from_dict['num_emails_sent'] - 1) * sent_sentiments[key] + extract['content-sentiment'][key]) / from_dict['num_emails_sent'], 4)
                from_dict['avg_sent_sentiment'] = sent_sentiments

        if 'avg_sent_content_length' in extractor.columns:
            # update sent content length
            from_dict['avg_sent_content_length'] = round(((from_dict['num_emails_sent'] - 1) * from_dict['avg_sent_content_length'] + extract['content-length']) / from_dict['num_emails_sent'], 4)

        # update global dictionary
        d[extract['to']] = to_dict
        d[extract['from']] = from_dict

    return d
