#!/usr/bin/python
import sys    
import time
import string
import private.pw
import datetime
from BridgeComm import BridgeComm
from ftplib import FTP
import StringIO
from ftplib import FTP

myComm = BridgeComm()

#myComm.send("boe","bah")
#myComm.send("boe","bah")
#myComm.send("12345678901234567","123456789012345678901234567890123")
#myComm.check_new_msg()
#myComm.check_new_msg()

while True:
    myFileIO = StringIO.StringIO()
    myComm.send("Temp?","-")
    #if myComm.check_new_msg():
    if myComm.wait_for_new_msg(10):
       print "New Temp received"
       print myComm.read_ID,myComm.read_command,myComm.read_value
       temp=myComm.read_value
    myComm.send("CO2?","-")
    if myComm.wait_for_new_msg(10):
       print "New CO2 pulses received"
       print myComm.read_ID,myComm.read_command,myComm.read_value
       pulses=myComm.read_value
    now=datetime.datetime.now()
    now_str=now.strftime("%Y-%m-%d %H:%M")
    myFileIO.write(now_str)
    myFileIO.write(",")
    myFileIO.write(temp)
    myFileIO.write(",")
    myFileIO.write(pulses)
    myFileIO.seek(0)
    ftp=FTP("ftp.homebrew.be")
    ftp.login(private.pw.myUser,private.pw.myPass)
    ftp.cwd("www.homebrew.be/Yafa")
    ftp.storlines("APPE dat.csv",myFileIO)
    ftp.close()
    myFileIO.close()
    time.sleep(301)
print end
