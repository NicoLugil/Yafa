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
from email.mime.text import MIMEText
import private.pw

def SendMail(tto, subject, body):
    USERNAME = private.pw.myMailUser
    PASSWORD = private.pw.myMailPass
    
    #msg = MIMEText('2nd mail Hello,\nMy name is Yun, \nhow are you')
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = USERNAME
    msg['To'] = tto
    
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo_or_helo_if_needed()
    server.starttls()
    server.ehlo_or_helo_if_needed()
    server.login(USERNAME,PASSWORD)
    server.sendmail(USERNAME, tto, msg.as_string())
    server.quit()
    
