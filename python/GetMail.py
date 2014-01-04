#!/usr/bin/python
import sys
import imaplib
import private.pw
import email

USERNAME = private.pw.myMailUser
PASSWORD = private.pw.myMailPass
MAILTO  = private.pw.myMailTo

imap_server = imaplib.IMAP4_SSL("imap.gmail.com",993)
imap_server.login(USERNAME, PASSWORD)
imap_server.select('INBOX')

result, data = imap_server.uid('search', None, "UNSEEN") # get unseen message UIDs
for my_uid in data[0].split():
   my_msg=''
   #result, data = imap_server.uid('fetch',my_uid, '(BODY.PEEK[HEADER.FIELDS (FROM)])')   # spaces are important here !!
   #result, data = imap_server.uid('fetch',my_uid, '(BODY.PEEK[])')   # use this if dont want to flag mail as seen
   result, data = imap_server.uid('fetch',my_uid, '(BODY[])')
   raw_email=data[0][1]
   email_msg = email.message_from_string(raw_email)
   maintype = email_msg.get_content_maintype()
   if maintype == 'multipart':
      for part in email_msg.get_payload():
         if part.get_content_maintype() == 'text':
            my_msg = part.get_payload()
   elif maintype == 'text':
     my_msg = email_msg.get_payload()
   print my_msg
imap_server.close()
imap_server.logout()


