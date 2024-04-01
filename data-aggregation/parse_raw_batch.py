"""
Script to decode scp'd raw email csvs
"""
import os
import numpy as np
import pandas as pd
import csv
from datetime import datetime
from tqdm import tqdm
import re


# specify batch number here, parsing to be done in batches
scp_path = './scp-results/batch'
batch = 3
archives_path = scp_path + str(batch) + '/'

# find file paths
batch_dirs = []
list_dirs = []
for subdir, dirs, files in os.walk(archives_path):
    for dir in dirs:
        batch_dirs.append(dir)
for batch_dir in batch_dirs:
    list_dirs.append((archives_path + batch_dir + '/', batch_dir))


# decode quoted printable text
def quoted_printable_decoding(text):
    # deal with edge case when there is no previous email in the chain, text = -1
    if isinstance(text, int) or isinstance(text, float):
        return text
    # if the email is too short, do not alter it
    if len(text) > 5:
        text = re.sub('=(0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F)(0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F)', '', text)
        text = re.sub('=', '', text)
    return text


# parsing function
def process_csv(file_path, listname):
    scp_df = pd.read_csv(file_path)
    # create new df in final form
    new_df = pd.DataFrame(columns=['list-name', 'id','to-name', 'to-address','from-name','from-address',
                                    'subject','date','content','parent-id', 'datetime-object', 'to', 'from'])

    # iterate through the scp'd content
    for index, row in tqdm(scp_df.iterrows()):
        # reformat date
        datetime_object = None
        try:
            datetime_object = datetime.strptime(row['date'], '%a, %d %b %Y %H:%M:%S %z')
        except:
            datetime_object = None

        # try to separate names from email addresses for 'to' column
        try:
            to_array = row['to'].split(' ')
            new_to_address = None
            new_to_name = None
            if len(to_array) == 1:
                new_to_address = to_array[0]
                new_to_name = None
            else:
                for s in to_array:
                    if '@' in s:
                        new_to_address = s
                        break
                if new_to_address:
                    to_array.remove(new_to_address)
                    new_to_name = ' '.join(to_array)
                # if couldn't find valid email address, keep separated
                else:
                    new_to_address, new_to_name = None, None
        except:
            new_to_address, new_to_name = None, None

        # try to separate name from address in 'from' column
        try:
            from_array = row['from'].split(' ')
            new_from_address = None
            new_from_name = None
            if len(from_array) == 1:
                new_from_address = from_array[0]
                new_from_name = None
            else:
                for s in from_array:
                    if '@' in s:
                        new_from_address = s
                        break
                if new_from_address:
                    from_array.remove(new_from_address)
                    new_from_name = ' '.join(from_array)
                # if could not find a valid email address, do not separate
                else:
                    new_from_address, new_from_name = None, None

            new_from_address = new_from_address.strip('<>"')
            new_to_address = new_to_address.strip('<>"')
        except:
            new_from_address, new_from_name = None, None

        # remove quoted printable encodings
        row_content = quoted_printable_decoding(row['content'])

        # if all of these are null, it is likely a blank row in the csv. Skip it
        if not datetime_object and not new_to_address and not new_to_name and not new_from_address and not new_from_name:
            continue

        # create new row in new df
        new_df.loc[len(new_df.index)] = [listname, row['id'], new_to_name, new_to_address,
                                        new_from_name, new_from_address, row['subject'],
                                        row['date'], row_content, row['parent-id'],
                                        datetime_object, row['to'], row['from']]

    return new_df


final_df = pd.DataFrame(columns=['list-name','id','to-name', 'to-address','from-name','from-address',
                                'subject','date','content','parent-id', 'datetime-object', 'to', 'from'])
# set maximum number of lists to preprocess
max_dirs = 15
counter = 0

for path, listname in tqdm(list_dirs):
    print("processing: " + listname)
    file_list = os.listdir(path)
    for file in file_list:
        df = process_csv(path + file, listname)
        final_df = pd.concat([final_df, df])
    counter += 1
    # set max_dirs to None to process the whole batch
    if max_dirs and counter > max_dirs:
        break

final_df.to_csv('./batch-emails/batch' + str(batch) + '.csv')
