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
    time.sleep(301)
    myFileIO = StringIO.StringIO()
    myComm.send("Temp?","-")
    #if myComm.check_new_msg():
    if myComm.wait_for_new_msg(10):
       now=datetime.datetime.now()
       now_str=now.strftime("%Y-%m-%d %H:%M")
       print now_str
       print "New Temp received"
       print myComm.read_ID,myComm.read_command,myComm.read_value
       myFileIO.write(now_str)
       myFileIO.write(" ")
       myFileIO.write(myComm.read_value)
       myFileIO.seek(0)
       ftp=FTP("ftp.homebrew.be")
       ftp.login(private.pw.myUser,private.pw.myPass)
       ftp.cwd("www.homebrew.be/Yafa")
       ftp.storlines("APPE temp.txt",myFileIO)
       ftp.close()
       myFileIO.close()


print end
