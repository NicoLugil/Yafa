#!/usr/bin/python
import sys    
import time
import string
import datetime
from ftplib import FTP
from subprocess import call
import StringIO

from BridgeComm import BridgeComm
from ParseSettings import ParseSettings
import private.pw

mySettings = ParseSettings()
mySettings.parse()

# reset mcu and establish connection
print "resetting mcu now"            
call(["reset-mcu"])                  
time.sleep(5)         
myComm = BridgeComm()
myComm.send("Init?","-")
if myComm.wait_for_new_msg(10):
   if myComm.read_command=="Init!":
     print "MCU OK!"
     # TODO: send some info or so
   else:
     print "MCU error: unexpexted response"
     print myComm.read_ID,myComm.read_command,myComm.read_value
     # TODO: error and use UnExp! from MCU side
     exit(1)
else:
   # TODO error
   print "MCU error no response"
   exit(1)


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
       print "cool_on=",cool_on
       heat_on=(int(myComm.read_value)>>10) & 1023
       print "heat_on=",heat_on
       total_on=(int(myComm.read_value)>>20) & 1023
       print "total_on=",total_on
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


