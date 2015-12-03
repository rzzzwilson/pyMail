import imaplib
import ConfigParser
import os

verbose = True

def open_connection(verbose=False):
    # Read the config file
    config = ConfigParser.ConfigParser()
    config.read([os.path.expanduser('./config')])

    # Connect to the server
    hostname = config.get('server', 'hostname')
    if verbose:
        print("Connecting to '%s'" % hostname)
    connection = imaplib.IMAP4_SSL(hostname)

    # Login to our account
    username = config.get('account', 'username')
    password = config.get('account', 'password')
    if verbose:
        print("Logging in as '%s'" % username)
    connection.login(username, password)
    return connection

if __name__ == '__main__':
    c = open_connection(verbose=True)
    try:
        print(str(dir(c)))
    finally:
        c.logout()
