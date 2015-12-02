pyMail
======
The code here is purely exploratory.

This is a Python+wxPython desktop application that runs under Linux, OSX
and Windows (7, at least).

It is possible I'll use pySide instead of wxPython.  We'll see.

The aim is to have enough functionality to replace my use of Thunderbird.
With Mozilla disowning Thunderbird it's probably time to move on.  I can't
find anything that looks usable, simple and is also free.  So I'll experiment
here and see if the idea goes anywhere.

Requirements
------------
* Python+wxPython.  This assumes python 2.7 and appropriate wxPython as
  wxPython for python 3 is not yet ready.  If pySide then maybe python 3.
* IMAP+SMTP protocol, targetted initially at GMail.
* Associated address book.
* Handle HTML email plus attachments.
* Address book has functionality close to that in Thunderbird.
* Save config and address book to separate files in a near-text form.
* The UI dedicates the maximum space to displaying the email body.

Nice to have?
-------------
* Links to environment calendar system.


Main Screen
-----------
```
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
```

The app will be driven by toolbar and menu.  Possibly also right-click
operations on individual headers.

We use a two pane view instead of the Thunderbird (and others) approach.
In that approach one pane is only to select a mailbox.  We can do that through
the toolbar.

What do we do if an email body has both plain text and HTML payloads?  Display
both, plain text only or HTML only?

How do we display/action attachments?

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
* 
* 
* 

There may be two (or more) address books.  One will be **the** address book.
The other will be a "collected" address book.  Receiving an email will
automatically put the received address into the "collected" address book.  It
will be possible to move one or more entries from "collected" to "main".

The address book should be kept on-disk in a form that lends itself to moving
address book data to another application.  Could have small apps that dump
the address book in various forms.

Writing email
-------------
The **To:** address field should auto-populate (from address book(s)) as the
address is typed (a la Thunderbird).

Must be able to send email in plain text as well as HTML.  The default should
be configurable.  Of course, sending in HTML will also send a plain text copy.

Must be able to attach files.

Speed
-----
Using IMAP doesn't make for a fast application.  Try keeping on-disk data
holding the latest 100 emails (for example).  Or keep state from previous
execution.  Don't download **all** emails, just what is shown in the headers
pane.

We will need to read emails in 'newest first' mode.

Enhancements
------------
If successful, expand pyMail to handle more than one mail server.  Either allow
the user to select the server or automatically combine all emails from all
servers.
