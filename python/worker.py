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
import os

from BridgeComm import BridgeComm
from ParseSettings import ParseSettings
from TimedActions import TimedActions
from GetMail import GetMail
from FtpStuff import directory_exists
from SendMail import SendMail
from ExceptionHandler import ExceptionHandler
import private.pw
import lib.pythonping
import wifiToolbox

import YafaGlobals
import threading

# some defines
SETTINGS_FILE = "/mnt/sda1/arduino/Yafa/settings.xml"

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

    print("worker started...")

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
    #   my_SendMail.SendNewMail("nico@lugil.be","Yun start","I started",my_logger)
    except Exception as e:
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
            print("MCU OK");
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

    myComm.send("TSensor?","-")
    if myComm.wait_for_new_msg(10,my_logger):
        if myComm.read_command=="TSensor!":
            if myComm.read_value=="ERROR":
                TsensMsg="ERROR: temperature sensor not found - actuators will be off!";
                my_SendMail.SendNewMail("nico@lugil.be","Yafa "+TsensMsg,TsensMsg,my_logger);
                print("TSensor ERROR")
            else:
                TsensMsg="OK: Addr={0}".format(myComm.read_value);
                print("TSensor OK! Addr={0}".format(myComm.read_value))
        else:
            my_logger.debug("MCU error: unexpexted response")
            # print myComm.read_ID,myComm.read_command,myComm.read_value
            # TODO: error and use UnExp! from MCU side
            exit(1)
    else:
        # TODO error
        my_logger.debug("MCU error no response")
        exit(1)

    wifi_info = "IP="+wifiToolbox.get_ip()+"   :  "+wifiToolbox.get_wifi_strength()

    try:
        mySettings = ParseSettings()
        mySettings.parse_file(SETTINGS_FILE,my_logger)
        my_SendMail.SendNewMail("nico@lugil.be","Yafa: started!",
                                "settings:\n" + 
                                "   dir name       = " +str(mySettings.name) + "\n" + 
                                "   temperature    = " +str(mySettings.temp) + "\n" +
                                "   clear          = " +str(mySettings.clear) + "\n" +
                                "   delta Heat ON  = " + str(mySettings.dHeat_on) + "\n" + 
                                "   delta Heat OFF = " + str(mySettings.dHeat_off) + "\n" + 
                                "   delta Cool ON  = " + str(mySettings.dCool_on) + "\n" + 
                                "   delta Cool OFF = " + str(mySettings.dCool_off) + "\n" +
                                "temperature sensor:\n  " +
                                TsensMsg + "\n"
                                "network:\n  " +
                                wifi_info + "\n"
                                ,my_logger)
    except Exception as e:
        # TODO: if this doesnt work: make sure user gets informed
        raise

    print "waiting for 5sec now"
    time.sleep(5)  # because I am slow in opening console :)

    #initial config - for now just temp stuff
    sendToSketch("setTemp=",mySettings.temp,my_logger,myComm)
    sendToSketch("setdHeatOn=",mySettings.dHeat_on,my_logger,myComm)
    sendToSketch("setdHeatOff=",mySettings.dHeat_off,my_logger,myComm)
    sendToSketch("setdCoolOn=",mySettings.dCool_on,my_logger,myComm)
    sendToSketch("setdCoolOff=",mySettings.dCool_off,my_logger,myComm)

    timer_log = TimedActions(301)
    timer_mail = TimedActions(61)
    timer_checkwifi = TimedActions(12)   # TODO put larger again
    timer_get_status = TimedActions(63)  
    timer_get_web_tasks = TimedActions(9)
    #timer_debug = TimedActions(15)

    my_cnt=0
    perc_cool=0.
    perc_heat=0.
    while True:
        try:
            time.sleep(4)
            #if timer_debug.enough_time_passed():
            #    myComm.send("CO2?","-")
            #    if myComm.wait_for_new_msg(10,my_logger):
            #        print("New CO2 pulses received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
            if timer_get_web_tasks.enough_time_passed():
                if not YafaGlobals.task_q.empty():
                    mySettings.temp=YafaGlobals.task_q.get()
                    sendToSketch("setTemp=",mySettings.temp,my_logger,myComm)
                    # write xml file 
                    # TODO: chekc if was parsed succesfully
                    mySettings.write_file(SETTINGS_FILE,my_logger)
                    my_SendMail.SendNewMail("nico@lugil.be","Yafa: temperature set to "+str(mySettings.temp),
                                            "delta Heat ON  = " + str(mySettings.dHeat_on) + "\n" + 
                                            "delta Heat OFF = " + str(mySettings.dHeat_off) + "\n" + 
                                            "delta Cool ON  = " + str(mySettings.dCool_on) + "\n" + 
                                            "delta Cool OFF = " + str(mySettings.dCool_off) + "\n" + 
                                            "settings should be saved",my_logger)
            if timer_checkwifi.enough_time_passed():
                try:
                    try:
                        ping_delay = lib.pythonping.do_one("192.168.1.1",5)
                    except Exception as e:
                        # if no network we arrive here
                        ping_delay=None
                    if ping_delay is None:
                        call(["wifi","down"], stdout=open(os.devnull, 'wb'))
                        time.sleep(5)
                        call("wifi", stdout=open(os.devnull, 'wb'))
                        time.sleep(5)
                        # TODO: keep track of this
                        #my_SendMail.SendNewMail("nico@lugil.be","Wifi has been restarted","Wifi restarted",my_logger)
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
                    # write xml file 
                    # TODO: chekc if was parsed succesfully
                    mySettings.write_file(SETTINGS_FILE,my_logger)
                    my_cnt=0   # quick hack for logging TODO

                    my_SendMail.SendNewMail("nico@lugil.be","Yafa: temperature set to "+str(mySettings.temp),
                                            "delta Heat ON  = " + str(mySettings.dHeat_on) + "\n" + 
                                            "delta Heat OFF = " + str(mySettings.dHeat_off) + "\n" + 
                                            "delta Cool ON  = " + str(mySettings.dCool_on) + "\n" + 
                                            "delta Cool OFF = " + str(mySettings.dCool_off) + "\n" + 
                                            "settings should be saved",my_logger)
            if timer_get_status.enough_time_passed():
                #TODO: raise if no response
                #      lock timeout?
                myComm.send("Temp?","-")
                if myComm.wait_for_new_msg(10,my_logger):
                    # TODO: check response comand!!!
                    YafaGlobals.lock_temperature.acquire()
                    try:
                        YafaGlobals.temperature=myComm.read_value
                    finally:
                        YafaGlobals.lock_temperature.release()
                else:
                    print "NO answer :("
            if timer_log.enough_time_passed():
                #TODO: raise if no response
                myStringIO = StringIO.StringIO()
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
                    ##print("New CO2 pulses received {0} {1} {2}".format(myComm.read_ID,myComm.read_command,myComm.read_value))
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
                myStringIO.write(now_str)
                myStringIO.write(",")
                myStringIO.write(mySettings.temp)
                myStringIO.write(",")
                myStringIO.write(temp)
                myStringIO.write(",")
                myStringIO.write(tmax)
                myStringIO.write(",")
                myStringIO.write(tmin)
                myStringIO.write(",")
                myStringIO.write(pulses)
                myStringIO.write(",")
                myStringIO.write(str(avg_act))
                myStringIO.write(",")
                myStringIO.write(str(perc_heat))
                myStringIO.write(",")
                myStringIO.write(str(perc_cool))
                myStringIO.seek(0)
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
                            ftp.storlines("STOR dat.csv",myStringIO)
                        else:
                            ftp.storlines("APPE dat.csv",myStringIO)
                        my_cnt=1
                    else:
                        ftp.cwd(mySettings.name)
                        ftp.storlines("APPE dat.csv",myStringIO)
                    ftp.close()
                except Exception as e:
                    e.args += ('happened while trying to ftp',)
                    raise
                myStringIO.close()
                sys.stdout.flush()
                my_SendMail.SendPendingMail(my_logger) # TODO: do less often
        except Exception as e:
            my_exc_handler.log_exception(e,my_logger,my_SendMail)
            #copyfile("/tmp/Yafa.log","/mnt/sda1/arduino/Yafa.log")
            #SendMail("nico@lugil.be","Yun Exception",str(message))

if __name__ == '__main__':
    main()
