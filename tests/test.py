#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import imaplib
import getpass
import email
import email.header
import datetime

import logger
log = logger.Log('test.log', logger.Log.DEBUG)

from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QWidget
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QIcon

EmailAccount = u'rzzzwilson@gmail.com'
EmailBox = u'INBOX'

InitialNumber = 20
MBPrefix = bytes('(\\HasNoChildren) "/" "', 'utf-8')


class EMailServer(object):

    Server = 'imap.gmail.com'

    def __init__(self, account, server=Server):
        self.selected = False
        self.mail_server = None
        password = self.get_password()
        if password is None:
            raise Exception('No password supplied')
        self.mail_server = imaplib.IMAP4_SSL(server)
        try:
            log('.login: EmailAccount=%s, password=%s' % (EmailAccount, password))
            (rv, data) = self.mail_server.login(EmailAccount, password)
        except imaplib.IMAP4.error:
            print('LOGIN FAILED!!!')
            sys.exit(1)
        log('Logged in successfuly')

    def get_mailboxes(self):
        """Get a list of avilable mailboxes."""

        result = []

        (rv, mailboxes) = self.mail_server.list()
        if rv == 'OK':
            for mb in mailboxes:
                if mb.startswith(self.mail_serverBPrefix):
                    mb_name = mb[len(self.mail_serverBPrefix):-1]
                    result.append(mb_name)

        log('get_mailboxes: returning:\n%s' % str(resut))

        return result

    def get_headers(self, mailbox, number=None):
        """Get a header list from mail server.

        mailbox  name of the mailbox to search
        number   if specified, only get this number, else get all

        Returns a list of tuples (id, header, datetime)
        where id        is the ID number of the email
              header    is a string containing header text
              datetime  a datetime object when email was received
        """

        (rv, data) = self.mail_server.select(mailbox)
        if rv != 'OK':
            raise Exception('Unable to open mailbox: %s' % rv)
        self.selected = True

        (rv, data) = self.mail_server.search(None, "ALL")
        if rv != 'OK':
            print('No messages found!')
            return

        ids = data[0].split()[-InitialNumber:]
        ids.reverse()

        result = []

        for num in ids:
            (rv, data) = self.mail_server.fetch(num, '(RFC822)')
            if rv != 'OK':
                raise Exception('ERROR getting message %s' % num)

            (num, subject, time) = self.get_email_header(num, data)
            result.append((num, subject, time))
#            local_time = time.strftime('%a, %d %b %Y %H:%M:%S')
#            print('Email %04d:%s\t%s' % (int(num), subject, time))

        log('get_headers: returning:\n%s' % str(result))

        return result

    def get_email_header(self, num, data):
        """Get an email header display string.

        num   unique ID of email message (string)
        data  data returned from a select()

        Returns a tuple (num, subject, datetime).
        """

        # get email subject
        s = str(data[0][1], 'utf-8')
        msg = email.message_from_string(s)
        decode = email.header.decode_header(msg['Subject'])[0]
        subject = decode[0]

        # get datetime convert to local datetime
        dtuple = email.utils.parsedate_tz(msg['Date'])
        dt = None
        if dtuple:
            ldt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(dtuple))

        # remove extraneous stuff in subject
        subject = subject.replace('\n', ' ')
        subject = subject.replace('\r ', '')

        log('get_email_header: returning %s' % str((num, subject, ldt)))

        return (num, subject, ldt)

    def get_password(self):
        (text, ok) = QInputDialog.getText(None, "Attention",
                                          "Password?", QLineEdit.Password)
        if ok and text:
            return text
        return None

    def __del__(self):
        if self.mail_server:
            self.mail_server.logout()
        if self.selected:
            self.mail_server.close()

class Window(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.button = QPushButton('Refresh')
        self.edit = QTextEdit()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.handleTest)

        log('About to setup the EMailServer')
        self.email_server =  EMailServer(EmailAccount)

        self.setGeometry(300, 300, 600, 300)
        self.setWindowTitle('Mail Headers')
        self.show()

    def handleTest(self):
        self.edit.setReadOnly(False)
        self.edit.clear()
        self.refresh()
        self.edit.setReadOnly(True)

    def refresh(self):
        hdrs = self.email_server.get_headers(EmailBox, number=10)
        for (id, header, datetime) in hdrs:
            self.edit.append(header)


if __name__ == '__main__':

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        import traceback

        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'
        log(msg)
        print(msg)
        sys.exit(1)

    # plug our handler into the python system
    sys.excepthook = excepthook

    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())


