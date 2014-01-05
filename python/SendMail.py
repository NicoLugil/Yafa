#!/usr/bin/python
import smtplib
from email.mime.text import MIMEText
import private.pw

def SendMail(To,Subject,Text):
   "sends mail"
   #msg = MIMEText('2nd mail Hello,\nMy name is Yun, \nhow are you')
   msg = MIMEText(Text)
   msg['Subject'] = Subject
   msg['From'] = private.pw.myMailUser
   msg['To'] = To
   
   server = smtplib.SMTP('smtp.gmail.com:587')
   server.ehlo_or_helo_if_needed()
   server.starttls()
   server.ehlo_or_helo_if_needed()
   server.login(private.pw.myMailUser,private.pw.myMailPass)
   server.sendmail(private.pw.myMailUser, To, msg.as_string())   # TODO: check if To is 'valid'
   server.quit()

