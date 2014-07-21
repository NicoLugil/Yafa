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

import sys    
import time
import string
import datetime
from ftplib import FTP
from subprocess import call
import StringIO
import logging
import logging.handlers

from BridgeComm import BridgeComm
from ParseSettings import ParseSettings
from TimedActions import TimedActions
from GetMail import GetMail
from FtpStuff import directory_exists
from SendMail import SendMail
import private.pw


def main():
    try: 

      # configure logging
      my_logger = logging.getLogger('MyLogger')
      my_logger.setLevel(logging.DEBUG)
      handler = logging.handlers.RotatingFileHandler("/tmp/Yafa.log", maxBytes=2048, backupCount=2)
      my_logger.addHandler(handler)
        
      SendMail("nico@lugil.be","Yun start","I started")

      mySettings = ParseSettings()
      mySettings.parse()
      
      # reset mcu and establish connection
      my_logger.debug("resetting mcu now")            
      call(["reset-mcu"])                  
      time.sleep(5)         
      myComm = BridgeComm()
      myComm.send("Init?","-")
      if myComm.wait_for_new_msg(10):
         if myComm.read_command=="Init!":
           my_logger.debug("MCU OK!")
           # TODO: send some info or so
         else:
           my_logger.debug("MCU error: unexpexted response")
           # print myComm.read_ID,myComm.read_command,myComm.read_value
           # TODO: error and use UnExp! from MCU side
           exit(1)
      else:
         # TODO error
         my_logger.debug("MCU error no response")
         exit(1)
      
      timer_log = TimedActions(301)
      timer_mail = TimedActions(61)
      
      
      my_cnt=0
      perc_cool=0.
      perc_heat=0.
      while True:
         time.sleep(10)
         if timer_mail.enough_time_passed():
            new_mail, msg = GetMail(my_logger)
            if new_mail:
               my_logger.debug(msg)
               sys.stdout.flush()
         if timer_log.enough_time_passed():
             myFileIO = StringIO.StringIO()
             myComm.send("Temp?","-")
             #if myComm.check_new_msg():
             if myComm.wait_for_new_msg(10):
                my_logger.debug("New Temp received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
                # TODO: check response comand!!!
                temp=myComm.read_value
             myComm.send("CO2?","-")
             if myComm.wait_for_new_msg(10):
                my_logger.debug("New CO2 pulses received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
                pulses=myComm.read_value
             myComm.send("Act?","-")
             if myComm.wait_for_new_msg(10):
                my_logger.debug("New Act values received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
                cool_on=int(myComm.read_value) & 1023
                my_logger.debug("cool_on={0}".format(cool_on))
                heat_on=(int(myComm.read_value)>>10) & 1023
                my_logger.debug("heat_on={0}".format(heat_on))
                total_on=(int(myComm.read_value)>>20) & 1023
                my_logger.debug("total_on={0}".format(total_on))
                if int(total_on)!=0:
                    perc_cool = cool_on/float(total_on)
                    perc_heat = heat_on/float(total_on)
                else:
                    perc_cool =float(0)
                    perc_heat =float(0)
                avg_act = perc_heat-perc_cool
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
                     my_logger.debug("dir" + str(mySettings.name) + "exists")
                 else:
                     my_logger.debug("dir" + str(mySettings.name) + "does not exist - creating it")
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
      template = "An exception of type {0} occured. Arguments:\n{1!r}"
      message = template.format(type(e).__name__, e.args)
      my_logger.debug("----")
      my_logger.debug(str(message))
      my_logger.debug("----")
      copyfile("tmp/Yafa.log","/mnt/sda1/arduino/Yafa.log")
      SendMail("nico@lugil.be","Yun Exception",str(message))
      raise
    my_logger.debug("end")

if __name__ == '__main__':
       main()
