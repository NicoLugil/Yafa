#!/usr/bin/python

# Copyright 2014 Nico Lugil 
#
# This file is part of Yafa!
#
# Yafa! is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yafa! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

# contact me at nico at lugil dot be 

import sys
import imaplib
import private.pw
import email
import feedparser
from email.utils import parseaddr

def GetMail():
   msg=""
   USERNAME = private.pw.myMailUser
   PASSWORD = private.pw.myMailPass

   # first check if there is new mail
   PROTO="https://"
   SERVER="mail.google.com"
   PATH="/gmail/feed/atom"

   n_email = int(feedparser.parse(PROTO + USERNAME + ":" + PASSWORD + "@" + SERVER + PATH)["feed"]["fullcount"])
   if n_email > 0:
      print "New mail!"
   else:
      print "No new mail!"
      return (False, msg)

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
      #f = open('workfile', 'w')
      #f.write(raw_email)
      #f.close()
      email_msg = email.message_from_string(raw_email)
      whofrom = email_msg.get_all('from', [])
      print whofrom[0]
      realname,mailaddr=email.utils.parseaddr(whofrom[0])
      print "here it is",mailaddr,"ok",realname,"rr"
      for part in email_msg.walk():
          # each part is a either non-multipart, or another multipart message
          # that contains further parts... Message is organized like a tree
          if part.get_content_type() == 'text/plain':
                msg=part.get_payload()

   imap_server.close()
   imap_server.logout()

   return (True,msg)

