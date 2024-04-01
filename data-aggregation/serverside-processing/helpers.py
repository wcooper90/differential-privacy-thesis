"""
Serverside processing helpers
"""
import re
import os
from tqdm import tqdm
import csv
import pprint
from constants import Constants
from objects import MessageObject


def is_this_message_nonsense(msg):
    for line in msg.split('\n'):
        for word in line.split(' '):
            # arbitrarily chosen threshold to determine when an email is full of nonsense
            if len(word) > 50:
                # a long word may be a link, so use this check. May not cover all cases but will cover most
                if 'http' not in word and 'www' not in word:
                    return True
    return False


def strip_replies(text):
    text = str(text)
    lines = text.split("\n")
    lines = [l for l in lines if len(l) > 0]
    no_replies = []
    for line in lines:
        if line[0] != ">":
            no_replies.append(line)

    no_replies_stripped = strip_response_footer(no_replies, response=False)

    return "\n".join(no_replies_stripped)


def find_carrots(text):
    text = str(text)
    lines = text.split("\n")
    lines = [l for l in lines if len(l) > 0]
    original_email_lines = []
    override_no_carrot = False
    for line in lines:
        if line[0] == ">":
            # this will cut off searching for content from a previous email once the footer is detected
            # unforunately this may lead to some issues if there is actually an underscore in the content
            # Not sure what the probability of this is but will have figure out how to deal with the edge cases
            if "_" in line[1:3]:
                break
            if ">" not in line[1:3]:
                original_email_lines.append(line)
            if line[-1] == '=':
                override_no_carrot = True

        # sometimes in printed-quoteable the next line in a previous email will not begin with a find_carrot
        # due to the '=' character on the previous line creating a soft line break
        # thus if one line that starts with a carrot ends with '=', we must append the next line even if
        # it does not have a carrot in front
        elif override_no_carrot:
            # reset this flag
            override_no_carrot = False
            # manually add the carrot
            original_email_lines.append("> " + line)
            # check again to see if this line ends with '='
            if line[-1] == '=':
                override_no_carrot = True

    if len(original_email_lines) == 0:
        return -1

    stripped_lines = strip_response_footer(original_email_lines)

    stripped_lines = "\n".join(stripped_lines)

    stripped_lines = stripped_lines.replace('\n', '').replace(' ', '')
    # return "\n".join(original_email_lines)
    return stripped_lines


def strip_response_footer(lines, response=True):
    new_lines = []
    for line in lines:

        # if the lines correspond to an email that is a response, strip the first carrot. If there is another space after that, remove it as well
        if response:
            line = line[1:]
            if line and line[0] == ' ':
                line = line[1:]
            else:
                continue

        # if we find footers of this form, end the message
        foot = []
        foot = re.findall("On (Sun|Mon|Tue|Wed|Thu|Fri|Sat|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", line)
        if foot:
            break

        # check to make sure this isn't removing too many actual email lines
        foot = re.findall("On (\d+/\d+/\d+),", line)
        if foot:
            break

        # remove quoting footers
        quote = []
        quote_email = []
        quote = re.findall("Quoting", line)
        quote_email = re.findall("(\w+@\w+\.\w+)", line)
        if quote and quote_email:
            break

        # remove this type of footer
        at = re.findall("At", line)
        date = re.findall('(\d+/\d+/\d+)', line)
        wrote = re.findall('wrote', line)
        if at and date and wrote:
            break


        # remove the forwarded message.
        # this may be interesting to examine in the future, if forwarded messages in a group are unusual
        forwarded_message = re.findall("Begin forwarded message:", line)
        if forwarded_message:
            break

        new_lines.append(line)
    return new_lines


def remove_r(text):
    return text.replace("\r", "")


def get_text(msg):
    while msg.is_multipart():
        msg = msg.get_payload()[0]
    return msg.get_payload()


def assign_message_object_attributes(new_email, msg):
    new_email.to = msg['to']
    new_email.from_ = msg['from']
    new_email.date = msg['date']
    new_email.subject = msg['subject']
    return new_email


def getbody(message): #getting plain text 'email body'
    body = None
    if message.is_multipart():
        for part in message.walk():
            if part.is_multipart():
                for subpart in part.walk():
                    if subpart.get_content_type() == 'text/plain':
                        body = subpart.get_payload(decode=True)
            elif part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True)
    elif message.get_content_type() == 'text/plain':
        body = message.get_payload(decode=True)
    return body


def quoted_printable_decoding(text):
    # deal with edge case when there is no previous email in the chain, text = -1
    if isinstance(text, int):
        return text
    # if the email is too short, do not alter it
    if len(text) > 5:
        text = re.sub('=(0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F)(0|1|2|3|4|5|6|7|8|9|A|B|C|D|E|F)', '', text)
        text = re.sub('=', '', text)
    return text


def process_email(msg):
    new_email = MessageObject()
    new_email = assign_message_object_attributes(new_email, msg)
    msg = get_text(msg)
    msg = remove_r(msg)
    msg = strip_replies(msg)
    if is_this_message_nonsense(msg):
        return None
    new_email.content = msg
    return new_email


def write_emails(list_name, message_objects, write_num, batch_num):
    csv_file = 'parsed-archives/batch' + str(batch_num) + '/' + list_name + '/' + list_name + '__' + str(write_num) + '.csv'
    try:
        with open(csv_file, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=Constants.email_csv_columns)
            writer.writeheader()
            for data in message_objects:
                writer.writerow(data.dictify())
    except IOError:
        print("I/O error")


def write_num_emails(list_name, num_emails, failures):
    csv_file = Constants.email_length_csv_path
    try:
        with open(csv_file, 'a') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames= Constants.email_length_columns)
            writer.writerow({'list-name': list_name, 'num-emails': num_emails, 'num-failed-parses': failures})
    except IOError:
        print("I/O error")
