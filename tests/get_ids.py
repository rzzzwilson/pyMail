#!/usr/bin/env python3

import sys
import imaplib
import getpass
import email
import email.header
import datetime

import logger
log = logger.Log('test.log', logger.Log.DEBUG)


EmailAccount = u'rzzzwilson@gmail.com'
EmailBox = u'INBOX'

InitialNumber = 20
MBPrefix = bytes('(\\HasNoChildren) "/" "', 'utf-8')


def get_email_header(M, num, data):
    """Get an email header display string.

    M     the mail server object
    num   unique ID of email message
    data  data returned from a select()

    Returns a tuple (subject, datetime).
    """

    s = str(data[0][1], 'utf-8')
    msg = email.message_from_string(s)
    decode = email.header.decode_header(msg['Subject'])[0]
    subject = decode[0]

    # Now convert to local date-time
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    local_time = None
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))

    # remove extraneous stuff in subject
    subject = subject.replace('\n', ' ')
    subject = subject.replace('\r ', '')

    return (subject, local_date)

def process_mailbox(M):
    """
    Do something with emails messages in the folder.
    For the sake of this example, print some headers.
    """

    (rv, data) = M.search(None, "ALL")
    if rv != 'OK':
        print('No messages found!')
        return

    ids = data[0].split()[-InitialNumber:]
    ids.reverse()

    for num in ids:
        (rv, data) = M.fetch(num, '(RFC822)')
        if rv != 'OK':
            print('ERROR getting message %d' % num)
            return
        (subject, time) = get_email_header(M, num, data)
        local_time = time.strftime('%a, %d %b %Y %H:%M:%S')
        print('Email %04d:%s\t%s' % (int(num), subject, time))


M = imaplib.IMAP4_SSL('imap.gmail.com')

try:
    (rv, data) = M.login(EmailAccount, getpass.getpass())
except imaplib.IMAP4.error:
    print('LOGIN FAILED!!!')
    sys.exit(1)

(rv, mailboxes) = M.list()
if rv == 'OK':
    print('Mailboxes:')
    for mb in mailboxes:
        print('mb=%s, type(mb)=%s' % (mb, type(mb)))
        if mb.startswith(MBPrefix):
            mb_name = mb[len(MBPrefix):-1]
            print('mb=%s, mb_name=%s' % (str(mb), mb_name))
    #print mailboxes

(rv, data) = M.select(EmailBox)
if rv == 'OK':
    print('Processing mailbox %s' % EmailBox)
    process_mailbox(M)
    M.close()
else:
    print('ERROR: Unable to open mailbox: %s', rv)

M.logout()
