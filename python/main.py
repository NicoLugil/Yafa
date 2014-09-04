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
from shutil import copyfile

from BridgeComm import BridgeComm
from ParseSettings import ParseSettings
from TimedActions import TimedActions
from GetMail import GetMail
from FtpStuff import directory_exists
from SendMail import SendMail
from ExceptionHandler import ExceptionHandler
import private.pw
import lib.pythonping

# some defines
SETTINGS_FILE = "/mnt/sda1/arduino/Yafa/settings.xml"

def setTemp(temp,my_logger,myComm):
    print "Sending setTemp command"
    myComm.send("setTemp=",str(temp))
    if myComm.wait_for_new_msg(10,my_logger):
        if myComm.read_command=="setTemp2":
            my_logger.debug("temp set OK!")
            # TODO: check temp value within apprximation
        else:
            print "got wrong setTemp ack:"+myComm.read_command
            my_logger.error("MCU error: unexpexted response-setTemp")
            # TODO: error 
            exit(1)
    else:
        # TODO error
        print "got no setTemp ack"
        my_logger.error("MCU error no response-setTemp")
        exit(1)

def sendToSketch(command,value,my_logger,myComm):
    print "Sending " + command + " command"
    myComm.send(command,str(value))
    if myComm.wait_for_new_msg(10,my_logger):
        if myComm.read_command==(command):
            my_logger.debug(command+"OK!")
            # TODO: check value within apprximation
        else:
            print "got wrong " + command + " ack:"+myComm.read_command
            my_logger.error("MCU error: unexpexted response-"+command)
            # TODO: error 
            exit(1)
    else:
        # TODO error
        print "got no " + command + " ack"
        my_logger.error("MCU error no response-"+command)
        exit(1)

def main():

    try:
        my_logger = logging.getLogger('MyLogger')
        my_logger.setLevel(logging.ERROR)
        handler = logging.handlers.RotatingFileHandler("/tmp/Yafa.log", maxBytes=16384, backupCount=2)
        formatter = logging.Formatter("%(asctime)s : %(levelname)s - %(message)s","%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        my_logger.addHandler(handler)
    except Exception as e:
        raise

    try:
        my_SendMail = SendMail()
        my_SendMail.SendNewMail("nico@lugil.be","Yun start","I started",my_logger)
    except Exception as e:
        raise

    try:
        mySettings = ParseSettings()
        mySettings.parse_file(SETTINGS_FILE,my_logger)
    except Exception as e:
        # TODO: if this doesnt work: make sure user gets informed
        raise

    my_exc_handler = ExceptionHandler(10,"main")

    # reset mcu and establish connection
    my_logger.debug("resetting mcu now")
    call(["reset-mcu"])
    time.sleep(5+6)
    myComm = BridgeComm()
    myComm.send("Init?","-")
    if myComm.wait_for_new_msg(10,my_logger):
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

    print "waiting for 5sec now"
    time.sleep(5)  # because I am slow in opening console :)

    #initial config - for now just temp
    sendToSketch("setTemp=",mySettings.temp,my_logger,myComm)

    timer_log = TimedActions(301)
    timer_mail = TimedActions(61)
    timer_checkwifi = TimedActions(30)

    my_cnt=0
    perc_cool=0.
    perc_heat=0.
    while True:
        try:
            time.sleep(10)
            if timer_checkwifi.enough_time_passed():
                try:
                    ping_delay = lib.pythonping.do_one("192.168.1.1",5)
                    if ping_delay is None:
                        SendMail("nico@lugil.be","Wifi lost","Wifi lost")
                        call(["wifi"])
                        time.sleep(20)
                except Exception as e:
                    e.args += ('happened while trying to checkwifi',)
                    raise
            if timer_mail.enough_time_passed():
                try:
                    new_mail, msg = GetMail(my_logger)
                except Exception as e:
                    e.args += ('happened while trying to GetMail',)
                    raise
                if new_mail:
                    # TODO: work out - for now very "dedicated"
                    my_logger.debug(msg)
                    sys.stdout.flush()
                    mySettings.parse_string(msg,my_logger)
                    sendToSketch("setTemp=",mySettings.temp,my_logger,myComm)
                    sendToSketch("setdHeatOn=",mySettings.dHeat_on,my_logger,myComm)
                    sendToSketch("setdHeatOff=",mySettings.dHeat_off,my_logger,myComm)
                    sendToSketch("setdCoolOn=",mySettings.dCool_on,my_logger,myComm)
                    sendToSketch("setdCoolOff=",mySettings.dCool_off,my_logger,myComm)
                    my_SendMail.SendNewMail("nico@lugil.be","Yafa: temperature set to "+str(mySettings.temp),
                                            "delta Heat ON  = " + str(mySettings.dHeat_on) + "\n" + 
                                            "delta Heat OFF = " + str(mySettings.dHeat_off) + "\n" + 
                                            "delta Cool ON  = " + str(mySettings.dCool_on) + "\n" + 
                                            "delta Cool OFF = " + str(mySettings.dCool_off) + "\n" + 
                                            "All other settings were ignored! Also settings were not saved",my_logger)
                    # TODO: write xml file if can be parsed succesfully
            if timer_log.enough_time_passed():
                #TODO: raise if no response
                myFileIO = StringIO.StringIO()
                myComm.send("Temp?","-")
                #if myComm.check_new_msg():
                if myComm.wait_for_new_msg(10,my_logger):
                    my_logger.debug("New Temp received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
                    # TODO: check response comand!!!
                    temp=myComm.read_value
                myComm.send("Tmax?","-")
                if myComm.wait_for_new_msg(10,my_logger):
                    my_logger.debug("New Tmax received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
                    # TODO: check response comand!!!
                    tmax=myComm.read_value
                myComm.send("Tmin?","-")
                if myComm.wait_for_new_msg(10,my_logger):
                    my_logger.debug("New Tmin received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
                    # TODO: check response comand!!!
                    tmin=myComm.read_value
                myComm.send("CO2?","-")
                if myComm.wait_for_new_msg(10,my_logger):
                    my_logger.debug("New CO2 pulses received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
                    pulses=myComm.read_value
                myComm.send("Act?","-")
                if myComm.wait_for_new_msg(10,my_logger):
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
                try:
                    now=datetime.datetime.now()
                except Exception as e:
                    e.args += ('happened while trying to get time now',)
                    raise
                now_str=now.strftime("%Y-%m-%d %H:%M")
                myFileIO.write(now_str)
                myFileIO.write(",")
                myFileIO.write(mySettings.temp)
                myFileIO.write(",")
                myFileIO.write(temp)
                myFileIO.write(",")
                myFileIO.write(tmax)
                myFileIO.write(",")
                myFileIO.write(tmin)
                myFileIO.write(",")
                myFileIO.write(pulses)
                myFileIO.write(",")
                myFileIO.write(str(avg_act))
                myFileIO.seek(0)
                try:
                    ftp=FTP("ftp.homebrew.be")
                    ftp.login(private.pw.myFtpUser,private.pw.myFtpPass)
                    ftp.cwd("www.homebrew.be/Yafa")
                    if my_cnt==0:
                        if directory_exists(mySettings.name,ftp):
                            my_logger.debug("dir " + str(mySettings.name) + " exists")
                        else:
                            my_logger.debug("dir " + str(mySettings.name) + " does not exist - creating it")
                            ftp.mkd(mySettings.name)
                        ftp.cwd(mySettings.name)
                        ftp.storbinary("STOR index.html",open("/mnt/sda1/arduino/Yafa/index.html","r"))
                        if mySettings.clear:
                            ftp.storlines("STOR dat.csv",myFileIO)
                        else:
                            ftp.storlines("APPE dat.csv",myFileIO)
                        my_cnt=1
                    else:
                        ftp.cwd(mySettings.name)
                        ftp.storlines("APPE dat.csv",myFileIO)
                    ftp.close()
                except Exception as e:
                    e.args += ('happened while trying to ftp',)
                    raise
                myFileIO.close()
                sys.stdout.flush()
                my_SendMail.SendPendingMail(my_logger) # TODO: do less often
        except Exception as e:
            my_exc_handler.log_exception(e,my_logger,my_SendMail)
            #copyfile("/tmp/Yafa.log","/mnt/sda1/arduino/Yafa.log")
            #SendMail("nico@lugil.be","Yun Exception",str(message))

if __name__ == '__main__':
    main()
