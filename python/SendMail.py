#!/usr/bin/python
import smtplib
from email.mime.text import MIMEText
import private.pw

USERNAME = private.pw.myMailUser
PASSWORD = private.pw.myMailPass
MAILTO  = private.pw.myMailUser #private.pw.myMailTo

msg = MIMEText('2nd mail Hello,\nMy name is Yun, \nhow are you')
msg['Subject'] = 'Mail from Yun 2'
msg['From'] = USERNAME
msg['To'] = MAILTO

server = smtplib.SMTP('smtp.gmail.com:587')
server.ehlo_or_helo_if_needed()
server.starttls()
server.ehlo_or_helo_if_needed()
server.login(USERNAME,PASSWORD)
server.sendmail(USERNAME, MAILTO, msg.as_string())
server.quit()

