"""
Main script to run on the Mailman server to batch together emails from individual text files on disk,
and to prepare for scp'ing.
"""
from objects import MboxReader
from helpers import *
import os
from tqdm import tqdm
import pprint
from constants import Constants
import sys
import time


def main(list_name, parsed_archives_root_path, batch_num):
    num_emails = 0
    writes = 0
    failures = 0
    pp = pprint.PrettyPrinter(indent=4)
    print("*"*20 + " Preprocessing beginning for list " + list_name + "... " + "*"*20)
    # some lists do not have an mbox file, just return
    if not os.path.exists('./' + list_name + '.mbox/' + list_name + '.mbox'):
        print("*"*20 + " List " + list_name + " does not have an mbox file. Aborting... " + "*"*20)
        return

    start = time.time()

    with MboxReader('./' + list_name + '.mbox') as mbox:
        if not os.path.exists(parsed_archives_root_path + 'batch' + str(batch_num) + '/' + list_name):
            # If it doesn't exist, create it
            os.makedirs(parsed_archives_root_path + 'batch' + str(batch_num) + '/' + list_name)
        else:
            # assume that if the path is there, the preprocessing has already been done
            print("*"*20 + " Preprocessing has already been completed for list " + list_name + "... " + "*"*20)
            return

        counter = 0
        messages = []
        messages_content_set = {}

        for message in tqdm(mbox, total=mbox.length):

            if isinstance(message, int):
                print('could not parse message')
                failures += 1
                continue

            parent_id = None
            text = get_text(message)
            previous_email_in_chain = find_carrots(text)
            previous_email_in_chain = quoted_printable_decoding(previous_email_in_chain)

            if previous_email_in_chain in messages_content_set:
                # set parent id of this message to the id of the message it's responding to
                parent_id = messages_content_set[previous_email_in_chain]['id']

            try:
                message_object = process_email(message)
            except:
                print('could not process email')
                failures += 1
                continue

            # this means there was an abnormally long gibberish looking word in the email, get rid of it
            if not message_object:
                # print('weird message')
                # print("*"*80)
                continue
            message_object.id = list_name + str(num_emails)
            message_object.parent_id = parent_id

            # decode message from quoted printing before appending to dictionary
            messages_content_set[quoted_printable_decoding(message_object.content.replace('\n', '').replace(' ', ''))] = {'id': message_object.id}

            messages.append(message_object)
            counter += 1
            num_emails += 1
            if counter % 1000 == 0:
                write_emails(list_name, messages, writes, batch_num)
                writes += 1
                messages = []


    # call write_emails() at the end to ensure the last num_emails%1000 messages are written
    write_emails(list_name, messages, writes, batch_num)
    end = time.time()
    print('Total number of emails in list: ' + str(mbox.length))
    print('Seconds elapsed to preprocess: ' + str(round(end - start, 3)))
    print('Size of message content dictionary: ' + str(sys.getsizeof(messages_content_set)))


    write_num_emails(list_name, mbox.length, failures)


batch_num = '2'
batch_path = './list-batches/' + str(batch_num) + '.txt'
parsed_archives_root_path = '../../parsed-archives/'
f = open(batch_path, 'r')
analyzed_list_count = 0
for line in f:
    if line == '\n':
        break
    main(line[:-1], parsed_archives_root_path, batch_num)
    analyzed_list_count += 1
    print()
    print("Analyzed " + str(analyzed_list_count) " out of 500 lists in this batch")


f.close()
