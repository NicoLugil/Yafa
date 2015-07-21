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

import io
import sys
import time
#import string
#import datetime
#from ftplib import FTP
from subprocess import call
#import StringIO
import logging
import logging.handlers
import copy
#from shutil import copyfile
##import os
#import threading

from ParseSettings import ParseSettings
from YafaSMTPHandler import YafaSMTPHandler
from TimedActions import CountDownTimer
from TimedActions import IntervalTimer
from GetMail import GetMail
#from FtpStuff import directory_exists
#from SendMail import SendMail
import lib.pythonping
import wifiToolbox


# this sript can work up to a point on my PC
PC=False
if PC:
    SETTINGS_FILE = "settings.ini"
else:
    SETTINGS_FILE = "/mnt/sda1/arduino/Yafa/settings.ini"
    from BridgeComm import BridgeComm

# TODO: lots of cleanup try/except : use more consistently

# TODO: see if YafaGlobals protected by lock everywhere + minimize time spent in it

def sendToSketch(command,value,myComm):
    try:
        my_logger = logging.getLogger('MyLogger')
        my_logger.debug("Sending " + command + " command")
        myComm.send(command,str(value))
        if myComm.wait_for_new_msg(10,my_logger):
            # this one only works for commands where the same is returned!!!
            if myComm.read_command==(command):
                my_logger.debug("    "+command+"OK!")
                # TODO: check value within approximation
            else:
                raise YafaWorkerException("MCU error: got wrong " + command + " ack:"+myComm.read_command)
        else:
            raise YafaWorkerException('MCU error no response after '+command)
    except Exception as e:
        my_logger.exception("Error in sending command to sketch")

def getFromSketch(command,myComm,expected_return_command):
    try:
        my_logger = logging.getLogger('MyLogger')
        my_logger.debug("getting from sketch: Sending " + command + " command")
        myComm.send(command,"-")
        if myComm.wait_for_new_msg(10,my_logger):
            # this one only works for commands where the same is returned!!!
            if myComm.read_command==expected_return_command:
                my_logger.debug("    "+command+"OK!")
                return myComm.read_value
            else:
                raise YafaWorkerException("MCU error: got wrong " + command + " ack:"+myComm.read_command)
        else:
            raise YafaWorkerException('MCU error no response after '+command)
    except Exception as e:
        my_logger.exception("Error in sending command to sketch")

def log_settings(the_settings,TsensMsg):
    my_logger = logging.getLogger('MyLogger')
    # get wifi info
    wifi_info = "IP="+wifiToolbox.get_ip()+"   :  "+wifiToolbox.get_wifi_strength()

    msg = "Yafa: started!\n" + "settings:\n" + "   name           = " +str(the_settings.name) + "\n" + "   temperature    = " +str(the_settings.temp) + "\n" + "   delta Heat ON  = " + str(the_settings.dHeat_on) + "\n" + "   delta Heat OFF = " + str(the_settings.dHeat_off) + "\n" + "   delta Cool ON  = " + str(the_settings.dCool_on) + "\n" + "   delta Cool OFF = " + str(the_settings.dCool_off) + "\n" + "temperature sensor:\n  " + TsensMsg + "\n" "network:\n  " + wifi_info + "\n"
    my_logger.info(msg)

def settings_tosketch(the_settings,myComm):
    my_logger = logging.getLogger('MyLogger')
    sendToSketch("setTemp=",the_settings.temp,myComm)
    sendToSketch("setdHeatOn=",the_settings.dHeat_on,myComm)
    sendToSketch("setdHeatOff=",the_settings.dHeat_off,myComm)
    sendToSketch("setdCoolOn=",the_settings.dCool_on,myComm)
    sendToSketch("setdCoolOff=",the_settings.dCool_off,myComm)
    my_logger.debug('all inital setting succesfully sent to sketch ')


###################################################################################################
###################################################################################################

class YafaWorkerException(Exception):
    pass

###################################################################################################
###################################################################################################
def main():

    import private.pw

    # setup logging
    logging.raiseExceptions=0   # error in logging will be suppressed
    my_logger = logging.getLogger('MyLogger')
    my_logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s : %(levelname)s - %(pathname)s : %(message)s ","%Y-%m-%d %H:%M:%S")
    file_handler = logging.handlers.RotatingFileHandler("/tmp/Yafa.log", maxBytes=16384, backupCount=2)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    smtp_handler = YafaSMTPHandler(("smtp.gmail.com",587),'yafa@lugil.be', ['nico@lugil.be'], 'Yafa logging message', (private.pw.myMailUser, private.pw.myMailPass))
    smtp_handler.setFormatter(formatter)
    smtp_handler.setLevel(logging.INFO)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.DEBUG)
    my_logger.addHandler(file_handler)
    my_logger.addHandler(smtp_handler)
    my_logger.addHandler(stream_handler)

    # create globals 
    try:
        import YafaGlobals # gets default settings in variable settings
    except Exception as e:
        my_logger.exception('importing essential vars at startup failed - exiting the program')
        return

    # read settings, and go to wait_for_start
    YafaGlobals.main_lock.acquire()
    try:
        try:
            myParser = ParseSettings()
            myParser.loadFile(SETTINGS_FILE,YafaGlobals.settings)
            YafaGlobals.mode=YafaGlobals.Mode.wait_for_start
        except Exception as e:
            my_logger.exception('reading settings at startup failed - trying to continue, probably with default settings')
    except Exception as e:
        raise
    finally:
        YafaGlobals.main_lock.release()

    # count down to run phase, and communicate with web stuff
    try:
        # init count down
        YafaGlobals.main_lock.acquire()
        try:
            myDownCount = CountDownTimer(YafaGlobals.timeleft)
            myDownCount.start()
        except Exception as e:
            raise
        finally:
            YafaGlobals.main_lock.release()
        while not myDownCount.is_time_passed():
            my_logger.debug('starting CountDown')
            time.sleep(3)
            YafaGlobals.main_lock.acquire()
            try:
                YafaGlobals.timeleft=int(myDownCount.get_remaining_time())
                if(YafaGlobals.mode==YafaGlobals.Mode.requested2run):
                    myDownCount.end()
                    YafaGlobals.timeleft=0
                    YafaGlobals.mode=YafaGlobals.Mode.run
                    local_copy_of_settings = copy.copy(YafaGlobals.settings)
            except Exception as e:
                raise
            finally:
                YafaGlobals.main_lock.release()
            if YafaGlobals.mode==YafaGlobals.Mode.run:
                # received new settings - save them
                myParser.saveFile(SETTINGS_FILE,local_copy_of_settings)
    except Exception as e:
        my_logger.exception('starting CountDown failed - skipping wait phase')

    # to run phase - copy settings to local var
    my_logger.info("going to run phase now")
    YafaGlobals.main_lock.acquire()
    try:
        YafaGlobals.timeleft=0
        YafaGlobals.mode=YafaGlobals.Mode.run
        local_copy_of_settings = copy.copy(YafaGlobals.settings)
    except Exception as e:
        raise
    finally:
        YafaGlobals.main_lock.release()

    # reset mcu and establish connection
    try:
        my_logger.debug("resetting mcu now")
        call(["reset-mcu"])
        time.sleep(5+6)
        myComm = BridgeComm()
        myComm.send("Init?","-")
        if myComm.wait_for_new_msg(10,my_logger):
            if myComm.read_command=="Init!":
                my_logger.debug("MCU OK!")
            else:
                raise YafaWorkerException('MCU error: unexpected response after Init? '+myComm.read_command)
                # TODO: error and use UnExp! from MCU side
        else:
            raise YafaWorkerException('MCU error no response after Init?')
    except:
        my_logger.exception('Resetting MCU failed - exiting')
        raise

    # get T sensor info
    try:
        TsensMsg="?"
        myComm.send("TSensor?","-")
        if myComm.wait_for_new_msg(10,my_logger):
            if myComm.read_command=="TSensor!":
                if myComm.read_value=="ERROR":
                    TsensMsg="ERROR: temperature sensor not found - actuators will be off!"
                    my_logger.error(TsensMsg)
                else:
                    TsensMsg="TSensor OK! Addr={0}".format(myComm.read_value)
                    my_logger.debug(TsensMsg)
            else:
                raise YafaWorkerException('MCU error: unexpected response after TSensor? '+myComm.read_command)
                # TODO: error and use UnExp! from MCU side
        else:
            raise YafaWorkerException('MCU error no response after TSensor?')
    except:
        my_logger.exception('problems finding T sensor - exiting')
        raise

    # inform about settings, etc...
    try:
        log_settings(local_copy_of_settings,TsensMsg)
    except Exception as e:
        my_logger.exception('cant inform about settings - exiting')
        raise 

    #print "waiting for 5sec now"
    #time.sleep(5)  # because I am slow in opening console :)

    #initial config - for now just temp stuff
    try:
        settings_tosketch(local_copy_of_settings,myComm)
    except Exception as e:
        my_logger.exception('problem sending initial settings to sketch - exiting')
        raise 

    # set timers for different kind of recurring tasks
    timer_log = IntervalTimer(301)
    timer_mail = IntervalTimer(61)
    timer_checkwifi = IntervalTimer(12)   # TODO put larger again
    timer_get_status = IntervalTimer(63)  
    timer_get_web_tasks = IntervalTimer(9)
    #timer_debug = IntervalTimer(15)

    my_cnt=0
    perc_cool=0.
    perc_heat=0.
    while True:
        try:
            time.sleep(2)  # TODO: shorter/longer?
            ## web stuff
            if timer_get_web_tasks.enough_time_passed():
                try:
                    YafaGlobals.main_lock.acquire()
                    try:
                        new_settings=False;
                        if(YafaGlobals.mode==YafaGlobals.Mode.requested2run):
                            YafaGlobals.mode=YafaGlobals.Mode.run
                            local_copy_of_settings = copy.copy(YafaGlobals.settings)
                            new_settings=True;
                    except Exception as e:
                        raise
                    finally:
                        YafaGlobals.main_lock.release()
                    if new_settings:
                        # write ini file 
                        myParser.saveFile(SETTINGS_FILE,local_copy_of_settings)
                        log_settings(local_copy_of_settings,TsensMsg)   # TODO: update TsensMsg
                except Exception as e:
                    my_logger.exception("problem checking web stuff")
            ## check wifi
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
                        # TODO: keep better track of this
                        my_logger.info('wifi lost and restarted')
                except Exception as e:
                    my_logger.exception("problem checking wifi")
            ## read current temperature
            if timer_get_status.enough_time_passed():
                try:
                    measured_temp = getFromSketch("Temp?",myComm,"Temp=")
                    YafaGlobals.lock_temperature.acquire()
                    try:
                        YafaGlobals.temperature=measured_temp
                    except:
                        raise
                    finally:
                        YafaGlobals.lock_temperature.release()
                except:
                    my_logger.exception("problem getting temperature from sketch")
            ## new ini file via mail?
            if timer_mail.enough_time_passed():
                try:
                    try:
                        new_mail, msg = GetMail()
                    except Exception as e:
                        my_logger.exception("problem with GetMail")
                    if new_mail:
                        # write mail to tmp file
                        with open(".mailed_settings","w") as text_file:
                            msg = msg.replace('\r','')
                            text_file.write(msg)
                        # try parsing it into YafaGlobals.settings
                        YafaGlobals.main_lock.acquire()
                        try:
                            try:
                                myParser = ParseSettings()
                                myParser.loadFile(".mailed_settings",YafaGlobals.settings)
                                # TODO: go to another phase? start right away?
                                local_copy_of_settings = copy.copy(YafaGlobals.settings)
                            except Exception as e:
                                my_logger.exception('parsing mail settings failed')
                        except Exception as e:
                            raise
                        finally:
                            YafaGlobals.main_lock.release()
                        try:
                            # try saving them
                            myParser.saveFile(SETTINGS_FILE,local_copy_of_settings)
                            log_settings(local_copy_of_settings,TsensMsg)   # TODO: update TsensMsg
                        except Exception as e:
                            my_logger.exception("problem saving new settings received by mail")
                except:
                    my_logger.exception("problem checking mail")
        except:
            my_logger.exception("Error in main loop, will try to continue")


"""
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
"""

if __name__ == '__main__':
    main()
