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

my_cnt=0
perc_cool=0.
perc_heat=0.
while True:
    myFileIO = StringIO.StringIO()
    myComm.send("Temp?","-")
    #if myComm.check_new_msg():
    if myComm.wait_for_new_msg(10):
       print "New Temp received" # TODO: check response comand!!!
       print myComm.read_ID,myComm.read_command,myComm.read_value
       temp=myComm.read_value
    myComm.send("CO2?","-")
    if myComm.wait_for_new_msg(10):
       print "New CO2 pulses received" # TODO: check response comand!!!
       print myComm.read_ID,myComm.read_command,myComm.read_value
       pulses=myComm.read_value
    myComm.send("Act?","-")
    if myComm.wait_for_new_msg(10):
       print "New Act values received" # TODO: check response comand!!!
       print myComm.read_ID,myComm.read_command,myComm.read_value
       cool_on=int(myComm.read_value) & 1023
       heat_on=(int(myComm.read_value)>>10) & 1023
       total_on=(int(myComm.read_value)>>20) & (1024*1023)
       if int(total_on)!=0:
           perc_cool = cool_on/float(total_on)
           perc_heat = heat_on/float(total_on)
           print "perc_cool=",perc_cool
           print "perc_heat=",perc_heat
       else:
           perc_cool =float(0)
           perc_heat =float(0)
       avg_act = perc_heat-perc_cool
       print "avg_act=",avg_act
    now=datetime.datetime.now()
    now_str=now.strftime("%Y-%m-%d %H:%M")
    myFileIO.write(now_str)
    myFileIO.write(",")
    myFileIO.write(temp)
    myFileIO.write(",")
    myFileIO.write(pulses)
    myFileIO.write(",")
    myFileIO.write(str(avg_act))
    myFileIO.seek(0)
    ftp=FTP("ftp.homebrew.be")
    ftp.login(private.pw.myUser,private.pw.myPass)
    ftp.cwd("www.homebrew.be/Yafa")
    if my_cnt==0:
        ftp.storlines("STOR dat.csv",myFileIO)
        my_cnt=1
    else:
        ftp.storlines("APPE dat.csv",myFileIO)
    ftp.close()
    myFileIO.close()
    time.sleep(301)
print end


