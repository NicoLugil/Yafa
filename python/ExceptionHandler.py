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

# Class to handle exceptions. For now very simple
# ideas:
#    keep in log, try to send via mail

import sys
import string
import time
import logging
import logging.handlers
import SendMail


## just an exception with a method that returns
## some special members (if given)
#class YafaException(Exception):
#    def __init__(self,severity)
#        pass
#def getSeverity():
#    pass
#
#


class ExceptionHandler:
    def __init__(self,max_exc_mail,name):
        self.n_exc=0
        self.max_exc_mail = max_exc_mail
        self.name = name
    def log_exception(self,e,my_logger,my_sendmail):
        template = "An exception of type {0} occured. Arguments:\n{1!r}"
        message = template.format(type(e).__name__, e.args)
        my_logger.error(str(message))
        if self.n_exc<self.max_exc_mail:
            self.n_exc = self.n_exc+1
            my_sendmail.SendNewMail("nico@lugil.be",self.name+":Yafa exception - "+str(self.n_exc),str(message),my_logger)
        else:
            if self.n_exc==self.max_exc_mail:
                self.n_exc = self.n_exc+1
                my_sendmail.SendNewMail("nico@lugil.be",self.name+":Yafa exception limit for mail","Maximum number of exceptions to mail reached",my_logger)



