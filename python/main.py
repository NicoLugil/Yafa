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

from bottle import run, route, get, post, request
import threading
import time
import copy

import YafaGlobals
import worker

my_error_message = "Oops something went wrong!"
full_wait_time = YafaGlobals.timeleft

#TODO: use templates

@route('/start')
def hello():
    return "Starting now..."

@route('/')
def root():
    # TODO: timeout ?
    try:
        YafaGlobals.main_lock.acquire()
        settings_copy=copy.copy(YafaGlobals.settings)
        mode_copy=copy.copy(YafaGlobals.mode)
        timeleft_copy=copy.copy(YafaGlobals.timeleft)
    except:
        return my_error_message+' : copy settings'
    finally:
        YafaGlobals.main_lock.release()
    try:
        msg="Current settings"
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    name: "+str(settings_copy.name)
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    temp: "+str(settings_copy.temp)
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    dHeat_on: "+str(settings_copy.dHeat_on)
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    dHeat_off: "+str(settings_copy.dHeat_off)
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    dCool_on: "+str(settings_copy.dCool_on)
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    dCool_off: "+str(settings_copy.dCool_off)
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    dCool_off: "+str(settings_copy.dCool_off)
        msg=msg+"</br>Current phase"
        msg=msg+"</br>&nbsp;&nbsp;&nbsp;    mode: "+str(mode_copy)
        if(mode_copy==YafaGlobals.Mode.boot):
            msg=msg+"</br></br> <b>booting busy...please refresh in a couple of seconds</b?"
        if(mode_copy==YafaGlobals.Mode.wait_for_start):
            msg=msg+"</br></br> <b>auto-start countdown busy"
            perc_rem=int(50.0*timeleft_copy/full_wait_time)
            msg = msg + "<pre><br>"
            # TODO: not sure this is 100% correct - good enough for now
            for x in range(0, perc_rem-1):
                msg = msg+'|'
            for x in range(0, 50-perc_rem-1):
                msg = msg+'-'
            msg = msg +'&nbsp;&nbsp;&nbsp;' + str(timeleft_copy) + '/'+str(full_wait_time)
            msg = msg + "</pre></b>"
            msg = msg + '<br/> you have 2 options:'
            msg = msg + '<br/>&nbsp;&nbsp;&nbsp;    1. do nothing - Yafa will start automatically at end of countdown with current settings'
            msg = msg + '<br/>&nbsp;&nbsp;&nbsp;    2. change settings <a href="/settings">here</a>, and start immediately'
        if(mode_copy==YafaGlobals.Mode.run):
            msg = msg + '<br/>Settings can be changed <a href="/settings">here</a>'
        if(mode_copy==YafaGlobals.Mode.requested2run):
            msg = msg + '<br/>will start asap...please refresh in a couple of seconds'
        return msg
    except:
        raise
    #return my_error_message # TODO: put back?

@get('/settings')
def settings():
    try:
        YafaGlobals.main_lock.acquire()
        settings_copy=copy.copy(YafaGlobals.settings)
    except:
        return my_error_message+' : copy settings'
    finally:
        YafaGlobals.main_lock.release()
    try:
        msg = '<form action="/settings" method="post">\n'
        msg = msg + '<br/>Name                  : <input name="name" type="text" value="'+str(settings_copy.name)+'" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>\n'
        msg = msg + '<br/>Desired temperature   : <input name="temp" type="text" value="'+str(settings_copy.temp)+'" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>\n'
        msg = msg + '<br/>Hysteresis Heat ON    : <input name="dHeat_on" type="text" value="'+str(settings_copy.dHeat_on)+'" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>\n'
        msg = msg + '<br/>Hysteresis Heat OFF   : <input name="dHeat_off" type="text" value="'+str(settings_copy.dHeat_off)+'" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>\n'
        msg = msg + '<br/>Hysteresis Cool ON    : <input name="dCool_on" type="text" value="'+str(settings_copy.dCool_on)+'" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>\n'
        msg = msg + '<br/>Hysteresis Cool OFF   : <input name="dCool_off" type="text" value="'+str(settings_copy.dCool_off)+'" style="text-align: right" onfocus="this.select()" onmouseup="return false"/>\n'
        msg = msg + '</br></br><input value="Set" type="submit" />'
        msg = msg + '</form>\n'
    except:
        raise
    return msg

@post('/settings') # or @route('/settings', method='POST')
def do_settings():
    try:
        new_settings = YafaGlobals.Settings()
        new_settings.name = (request.forms.get('name'))
        new_settings.temp = float(request.forms.get('temp'))
        new_settings.dHeat_on = float(request.forms.get('dHeat_on'))
        new_settings.dHeat_off = float(request.forms.get('dHeat_off'))
        new_settings.dCool_on = float(request.forms.get('dCool_on'))
        new_settings.dCool_off = float(request.forms.get('dCool_off'))
    except Exception as e:
        return "Unable to parse settings: "+str(e)
    try:
        YafaGlobals.main_lock.acquire()
        YafaGlobals.settings.name=new_settings.name
        YafaGlobals.settings.temp=new_settings.temp
        YafaGlobals.settings.dHeat_on=new_settings.dHeat_on
        YafaGlobals.settings.dHeat_off=new_settings.dHeat_off
        YafaGlobals.settings.dCool_on=new_settings.dCool_on
        YafaGlobals.settings.dCool_off=new_settings.dCool_off
        YafaGlobals.mode=YafaGlobals.Mode.requested2run 
    except Exception as e:
        return my_error_message+' : copy settings to global ' + str(e)
    finally:
        YafaGlobals.main_lock.release()
    return 'Settings changed! Back to <a href="/">root</a>'

"""
@route('/status')
def status():
    # TODO: timeout ?
    YafaGlobals.lock_temperature.acquire()
    try:
        return "Temperature="+str(YafaGlobals.temperature)
    finally:
        YafaGlobals.lock_temperature.release()

@post('/settings') # or @route('/settings', method='POST')
def do_settings():
    temp = request.forms.get('temp')
    YafaGlobals.task_q.put(temp)
    return "<p>You succesfully set the temperature to "+str(temp)+"</p>"
"""

def main():


    # start worker
    threads=[]
    t=threading.Thread(target=worker.main)
    t.setDaemon(True)
    threads.append(t)
    t.start();
    time.sleep(5) # quick 'hack' to get worker going (reading settings, etc...)

    run(host='0.0.0.0', port=48963, debug=True)

    print "Oops server crashed!!"

    while True:
        # dont want things to end - for now this stupidity
        time.sleep(10)

#        try:
#            #TODO: no more debug
#            run(host='0.0.0.0', port=48963, debug=True)
#        except Exception as e:
#            print "Oops server crashed!!"
#            time.sleep(4)
#            # TODO


if __name__ == '__main__':
    main()




