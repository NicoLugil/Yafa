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

import smtplib
import time
from email.mime.text import MIMEText
import private.pw
from TimedActions import TimedActions
from ExceptionHandler import ExceptionHandler

class SendMail:
    def __init__(self):
        self.toSend = []
        self.timer = TimedActions(0);
        self.exc_handler = ExceptionHandler(10,"SendMail")
    def PendingMailsToSend(self):
        if len(self.toSend) != 0:
            return True
        else:
            return False
    def SendPendingMail(self,my_logger):
        try:
            my_logger.debug("SendPendingMail:")
            if self.timer.enough_time_passed():
                #print "   timer OK"
                my_logger.debug("   timer OK!")
                self.timer.set_interval(0)
                USERNAME = private.pw.myMailUser
                PASSWORD = private.pw.myMailPass
                server = smtplib.SMTP('smtp.gmail.com:587')
                server.ehlo_or_helo_if_needed()
                server.starttls()
                server.ehlo_or_helo_if_needed()
                server.login(USERNAME,PASSWORD)
                #print "before loop: len = "+str(len(self.toSend))
                while self.toSend:
                    item = self.toSend[0]
                    msg = MIMEText(item[2])
                    msg['Subject'] = item[1]
                    msg['From'] = USERNAME
                    msg['To'] = item[0]
                    server.sendmail(USERNAME, item[0], msg.as_string())
                    del self.toSend[0]
                server.quit()
                if len(self.toSend) != 0:
                    self.toSend = []
                    raise Exception("Unexpected len(self.toSend) != 0 in SendMail (len="+str(len(self.toSend))+")")
            else: 
                my_logger.debug("   waiting for timer to end, time remaining={0}s".format(self.timer.get_remaining_time()))
                #print "   waiting for timer to end, time remaining={0}s".format(self.timer.get_remaining_time())
        except Exception as e:
            # didnt manage to send all mails - put timer and hope when timer end all works
            e.args += ('happened while inside SendPendingMail',)
            self.timer.set_interval(120)
            self.timer.reset_timer()
            #self.exc_handler.log_exception(e,my_logger,self)   --> bit silly to send mail that mail failed TODO: log it and send later or so
            self.exc_handler.log_exception(e,my_logger,None)
    def SendNewMail(self,tto,subject,body,my_logger):
        # TODO: max size
        tup = (tto, time.strftime("%d/%m/%Y %H:%M:%S: ")+subject, body)
        self.toSend.append(tup)
        #print "SendNewMail added to toSend: "+str(tup)+". Total mails to send: "+str(len(self.toSend))+"."
        self.SendPendingMail(my_logger)




