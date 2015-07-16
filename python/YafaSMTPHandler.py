#!/usr/bin/python

# Copyright 2014 Nico Lugil <nico at lugil dot be>
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
# along with Yafa. If not, see <http://www.gnu.org/licenses/>.

import logging
import logging.handlers
from SendMail import SendMail
import collections
import time

class YafaSMTPHandler(logging.handlers.SMTPHandler):
    def __init__(self,mailhost,fromaddr,toaddrs,subject,credentials=None):
        logging.handlers.SMTPHandler.__init__(self,mailhost,fromaddr,toaddrs,subject,credentials)
        self.dq_size=2 # TODO make parameter
        self.notDelivered = collections.deque(maxlen=self.dq_size) 
        self.lostForever=0
        self.myMailer = SendMail()
    def configMailer(self):
            import string
            self.myMailer.sender = self.fromaddr  # no tuple needed - see SendMail defaults?
            self.myMailer.recipients = self.toaddrs  # no tuple needed - see SendMail defaults?
            self.myMailer.smtp_host = self.mailhost
            self.myMailer.smtp_login = self.username
            self.myMailer.smtp_password = self.password
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            self.myMailer.smtp_port = port
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = self.date_time
    def tryDelivery(self):
        try:
            if self.notDelivered:
                self.configMailer()
                l=len(self.notDelivered)
                msg = ['These {0} messages could not be delivered previously\n\n'.format(l)]
                for idx, item in enumerate(self.notDelivered):
                    msg.append("\n============== {0} ================\n\n".format(idx))
                    msg.append('Time: '+item[1]+'\n')
                    msg.append('Not delivered because: '+str(item[0])+'\n')
                    msg.append('Subject: '+item[2]+'\n')
                    msg.append('Message: '+item[3]+'\n')
                #print(msg)
                subj='Previously undeliverable messages ({0})'.format(l)
                #print(subj)
                self.myMailer.SendMessage(subj,''.join(msg))
                self.notDelivered.clear()
        except Exception as e:
            print('oops this went wrong')
            print e
            pass # we will try again later
    def emit(self, record):
        try:
            self.configMailer()
            msg = self.format(record)
            #raise Exception('boe')
            self.myMailer.SendMessage(self.getSubject(record),msg)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            # TODO: set raiseException correctly 
            # TODO: log what we dont log here
            t=time.strftime("%d/%m/%Y %H:%M:%S: ")
            if len(self.notDelivered)>=self.dq_size:
                self.lostForever=self.lostForever+1
            self.notDelivered.append((e,t,self.getSubject(record),msg))
            self.handleError(record)



