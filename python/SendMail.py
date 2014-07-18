#!/usr/bin/python
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
    
