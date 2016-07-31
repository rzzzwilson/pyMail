#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import imaplib
import getpass
import email
import email.header
import datetime
import pickle
import time

import logger
log = logger.Log('test.log', logger.Log.DEBUG)

from PyQt5.QtCore import QThread , pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit, QWidget
from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QIcon

EmailAccount = u'rzzzwilson@gmail.com'
EmailBox = u'INBOX'

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
            log('Logging to %s' % EmailAccount)
            (rv, data) = self.mail_server.login(EmailAccount, password)
        except imaplib.IMAP4.error:
            print('LOGIN FAILED!!!')
            sys.exit(1)
        log('Logged in successfuly')

        # now retrieve any saved state
        self.headers = self.get_saved_headers()
        log('__init__: self.headers=%s' % str(self.headers))

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

        ids = data[0].split()
        ids.reverse()

        result = []

        for num in ids:
            (rv, data) = self.mail_server.fetch(num, '(RFC822)')
            if rv != 'OK':
                raise Exception('ERROR getting message %s' % num)

            (num, subject, frm, time) = self.get_email_header(num, data)
            result.append((num, subject, frm, time))
#            local_time = time.strftime('%a, %d %b %Y %H:%M:%S')
#            print('Email %04d:%s\t%s' % (int(num), subject, time))

        log('get_headers: returning %d headers' % len(result))

        return result

    def get_email_header(self, num, data):
        """Get an email header display string.

        num   unique ID of email message (string)
        data  data returned from a select()

        Returns a tuple (num, subject, frm, datetime).
        """

        #log.dump_hex('Email body, data[0][1]', data[0][1])
        #log.dump_hex('Email body, data[0]', data[0])

        # get email subject
        log.dump_hex('Email body, data[0][1]', data[0][1])
        #s = str(data[0][1], 'utf-8')
        s = str(data[0][1], encoding='utf-8', errors='ignore')
        msg = email.message_from_string(s)
        if msg['Subject'] is None:
            msg['Subject'] = ''
        decode = email.header.decode_header(msg['Subject'])[0]
        subject = decode[0]
        decode = email.header.decode_header(msg['From'])[0]
        frm = decode[0]

        # get datetime convert to local datetime
        dtuple = email.utils.parsedate_tz(msg['Date'])
        dt = None
        if dtuple:
            ldt = datetime.datetime.fromtimestamp(email.utils.mktime_tz(dtuple))

        # remove extraneous stuff in subject
        log('type(subject)=%s' % type(subject))
        log('subject=%s' % subject)
        subject = subject.replace('\n', ' ')
        subject = subject.replace('\r ', '')

        log('get_email_header: returning %s' % str((num, subject, frm, ldt)))

        return (num, subject, frm, ldt)

    def get_password(self):
        (text, ok) = QInputDialog.getText(None, "Attention",
                                          "Password?", QLineEdit.Password)
        if ok and text:
            return text
        return None

    def __del__(self):
        pass

    def get_saved_headers(self):
        """Retrieve any saved headers from disk."""

        try:
            with open('headers.save', 'rb') as fd:
                return pickle.load(fd)
        except FileNotFoundError:
            return []

    def put_saved_headers(self, obj):
        """Save headers to disk."""

        log('put_saved_headers: Saving obj=%s' % str(obj))

        with open('headers.save', 'wb') as fd:
            pickle.dump(obj, fd)


class Window(QWidget):
    finished = pyqtSignal(int)

    def __init__(self):
        QWidget.__init__(self)
        layout = QVBoxLayout(self)
        self.button = QPushButton('Get Messages')
        self.edit = QTextEdit()
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.handleTest)

        log('About to setup the EMailServer')
        self.email_server = EMailServer(EmailAccount)

        self.setGeometry(100, 100, 900, 600)
        self.setWindowTitle('Mail Headers')
        self.show()

        self.update_headers(self.email_server.headers)
#        self.start_worker()

    def handleTest(self):
        self.edit.setReadOnly(False)
        self.edit.clear()
        self.refresh()
        self.edit.setReadOnly(True)

    def refresh(self, latest=None):
        """Get all headers after given ID.

        latest  ID of last received email
        """

        if latest is None:
            headers = self.email_server.get_headers(EmailBox)
        else:
            headers = self.email_server.get_headers(EmailBox)
        log('refresh: headers=%s' % str(headers))
        self.email_server.put_saved_headers(headers)
        self.update_headers(headers)

    def update_headers(self, headers):
        for (id, header, frm, datetime) in headers:
            self.edit.append(header + ' ' + frm)

    def start_worker(self):
        log('start_worker: starting')
        self.thread = QThread()
        self.finished[int].connect(self.refresh_box)
        self.thread.started.connect(self.get_all_headers)
        self.thread.start()

    @pyqtSlot(int)
    def refresh_box(self, i):
        log("refresh_box: Base caught finished, {}".format(i))

    def get_all_headers(self, result=42):
        log("Worker work")
        self.refresh()
        self.finished.emit(result)


if __name__ == '__main__':
    import traceback

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
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


