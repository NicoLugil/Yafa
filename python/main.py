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
from TimedActions import TimedActions
from GetMail import GetMail
from FtpStuff import directory_exists
from SendMail import SendMail
import private.pw

GetMail()

# TODO: replace print to logging system with rotating files

def main():
    try: 
      SendMail("nico@lugil.be","Yun start","I started")

      mySettings = ParseSettings()
      mySettings.parse()
      
      # reset mcu and establish connection
      print "resetting mcu now"            
      sys.stdout.flush()
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
      
      timer_log = TimedActions(301)
      timer_mail = TimedActions(61)
      
      
      my_cnt=0
      perc_cool=0.
      perc_heat=0.
      while True:
         time.sleep(10)
         if timer_mail.enough_time_passed():
            new_mail, msg = GetMail()
            if new_mail:
               print msg
               sys.stdout.flush()
         if timer_log.enough_time_passed():
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
             ftp.login(private.pw.myFtpUser,private.pw.myFtpPass)
             ftp.cwd("www.homebrew.be/Yafa")
             if my_cnt==0:
                 if directory_exists(mySettings.name,ftp):
                     print "dir",mySettings.name,"exists"
                 else:
                     print "dir",mySettings.name, "does not exist - creating it"
                     ftp.mkd(mySettings.name)
                 ftp.cwd(mySettings.name)
                 ftp.storbinary("STOR index.html",open("index.html","r"))
                 ftp.storlines("STOR dat.csv",myFileIO)
                 my_cnt=1
             else:
                 ftp.cwd(mySettings.name)
                 ftp.storlines("APPE dat.csv",myFileIO)
             ftp.close()
             myFileIO.close()
             sys.stdout.flush()
    except Exception as e:
      SendMail("nico@lugil.be","Yun Exception",str(e.args))
    print "end"

if __name__ == '__main__':
       main()
