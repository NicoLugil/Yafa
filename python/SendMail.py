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

import time
import private.pw
import pyzmail


class SendMail:
    def __init__(self):
        # TODO: make these settings configurable
        self.sender = (u'Yafa!', 'yafa@lugil.be')
        self.recipients = [(u'Nico Lugil', 'nico@lugil.be')]
        self.default_charset = 'iso-8859-1'
        self.encoding = 'us-ascii'
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587
        self.smtp_mode = 'tls'
        self.smtp_login= private.pw.myMailUser
        self.smtp_password= private.pw.myMailPass
    def SendMessage(self,subject,msg):
        payload, mail_from, rcpt_to, msg_id=pyzmail.compose_mail(self.sender, self.recipients, unicode(subject), self.default_charset, (msg, self.encoding))
        ret=pyzmail.send_mail(payload, mail_from, rcpt_to, self.smtp_host, self.smtp_port, self.smtp_mode, self.smtp_login, self.smtp_password)
        if isinstance(ret, dict):
            if ret:
                str = 'failed recipients:'+', '.join(ret.keys())
                raise SendMail.SendMailException(str)
            #    print 'failed recipients:', ', '.join(ret.keys())
            #else:
            #    print 'success'
        else:
            str = 'error:'+ret
            raise SendMail.SendMailException(str)
    class SendMailException(Exception):
        pass


