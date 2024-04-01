"""
Mailman GNU metadata header constants
"""
class Constants():
    email_csv_columns = ['id', 'to', 'from', 'subject', 'date', 'content', 'parent-id']
    mbox_keys = ['X-GM-THRID', 'X-Gmail-Labels', 'Delivered-To', 'Received', 'X-Received',
                 'ARC-Seal', 'ARC-Message-Signature', 'ARC-Authentication-Results',
                'Return-Path', 'Received', 'Received-SPF', 'Authentication-Results',
                'DKIM-Signature', 'X-Google-DKIM-Signature', 'X-Gm-Message-State',
                'X-Google-Smtp-Source', 'MIME-Version', 'X-Received', 'Date', 'Reply-To',
                 'X-Google-Id', 'Precedence', 'List-Unsubscribe', 'Feedback-ID', 'List-Id',
                 'X-Notifications', 'X-Notifications-Bounce-Info', 'Message-ID', 'Subject',
                 'From', 'To', 'Content-Type']

    email_length_csv_path = 'metadata/num_emails.csv'
    email_length_columns = ['list-name', 'num-emails', 'num-failed-parses']
