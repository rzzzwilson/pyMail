pyMail
======
The code here is purely exploratory.

This is a Python+PyQt5 desktop application that runs under Linux, OSX
and Windows (7, at least).

We'll use PyQt5.  This means we can use Python 3.  I've waited long enough
for wxPython to be compatible with Python 3.

The aim is to have enough functionality to replace my use of Thunderbird.
With Mozilla disowning Thunderbird it's probably time to move on.  I can't
find anything that looks usable, simple and is also free.  So I'll experiment
here and see if the idea goes anywhere.

Requirements
------------
* Python3+PyQt5.
* IMAP+SMTP protocol, targetted initially at GMail servers.
* Associated address book.
* Handle HTML email plus attachments.
* Address book has functionality close to that in Thunderbird.
* Save config and address book to separate files in a near-text form.
* The UI dedicates the maximum space to displaying the email body.

Will need to check Python 3 compatability with other requirements such as:

* imaplib
* email

Nice to have?
-------------
* Links to environment calendar system.


Main Screen
-----------

::

    +------------------------------------------------------------------------+
    | toolbar                                                                |
    +========================================================================+
    |                                                                        |
    |                                                                        |
    | headers (one line per email)                                           |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    +------------------------------------------------------------------------+
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    | body of selected email in headers pane                                 |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    |                                                                        |
    +------------------------------------------------------------------------+

The app will be driven by toolbar and menu.  Possibly also right-click
operations on individual headers.

We use a two pane view instead of the Thunderbird (and others) three pane
approach.  In that approach one pane is only to select a mailbox.  We can do
that through the toolbar.

The toolbar will have:

* two "buttons" in the toolbar to select server and mailbox.
  The left-most shows the server and the second shows the mailbox.
* a "delete" button to delete currently selected email
* a "reply" button ...
* a "forward" button ...

What do we do if an email body has both plain text and HTML payloads?  Display
both, plain text only or HTML only?

How do we display/action attachments?

The hardest part that I see (so far) is rendering the email body, including
attachments (if any).

How much state do we maintain between app invocations?  Do we remember which
email header+body is being displayed?

Address Book
------------
The address book will contain the following fields:

* Given name
* Full name
* Address
* Email address
* Phone address
* Skype ID
* Birthday
* Residential Address
* Photo?

There may be two (or more) address books.  One will be **the** address book.
The other will be a "collected" address book.  Receiving an email will
automatically put the received address into the "collected" address book.  It
will be possible to move one or more entries from "collected" to "main".

The address books should be kept on-disk in a form that lends itself to moving
address book data to another application.  Could have small apps that dump
the address book in various forms.

Writing email
-------------
The **To:** address field should auto-populate (from address book(s)) as the
address is typed (a la Thunderbird).

Must be able to send email in plain text as well as HTML.  The default should
be configurable.  Of course, sending in HTML will also send a plain text copy.
The question now is how much *HTML stuff* should we allow the email composer to
fiddle with.  Bold/Italic/URL...?

Must be able to attach files.

Speed
-----
Using IMAP doesn't make for a fast application.  Try keeping on-disk data
holding the latest 100 emails (for example).  Or keep state from previous
execution.  Don't download **all** emails, just what is shown in the headers
pane.

We will need to read emails in 'newest first' mode.

Roadmap
-------
We will approach a final product in stages:

* Display 10 latest headers of INBOX
* Display *all* headers in INBOX, on-demand while scrolling
* Allow user to select other mailbox, display headers
* Display unread email headers in bold, IMAP supports 'unread' attribute?
* Display simple text email body
* Display simple email body with attachment(s)
* Display HTML email body
* Display HTML email body with attachments(s)
* Allow right-click operations on header: delete, mark unread, move to ..., etc
* Allow compose and send of new email (no HTML or attachments)
* Allow attachments in new email
* Allow user to reply to email
* New email automatically populates the collected address book
* Email compose uses address books to autocomplete **To:** field
* etc, ...

We will use the GitHub issue system to control this.  The open issue with a
title starting **TARGET:** will contain the target state we are currently
aiming for.

If successful, expand pyMail to handle more than one mail server.  How are we
going to handle this:

* Mail from all servers goes into header pane
* Select server and repopulate display panes
