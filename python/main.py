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

@route('/hello')
def hello():
    return "Hello!"

@route('/status')
def status():
    # TODO: timeout ?
    try:
        YafaGlobals.main_lock.acquire()
        settings_copy=copy.copy(YafaGlobals.settings)
    except:
        return my_error_message+' : copy settings'
    finally:
        YafaGlobals.main_lock.release()
    try:
        msg="Current settings"
        msg=msg+"</br> name: "+str(settings_copy.name)
        msg=msg+"</br> temp: "+str(settings_copy.temp)
        msg=msg+"</br> dHeat_on: "+str(settings_copy.dHeat_on)
        msg=msg+"</br> dHeat_off: "+str(settings_copy.dHeat_off)
        msg=msg+"</br> dCool_on: "+str(settings_copy.dCool_on)
        msg=msg+"</br> dCool_off: "+str(settings_copy.dCool_off)
        return msg
    except:
        raise
        #return my_error_message

"""
@route('/status')
def status():
    # TODO: timeout ?
    YafaGlobals.lock_temperature.acquire()
    try:
        return "Temperature="+str(YafaGlobals.temperature)
    finally:
        YafaGlobals.lock_temperature.release()

@get('/settings')
def settings():
    Tset='?'
    YafaGlobals.lock_current_settings.acquire()
    try:
        Tset=str(YafaGlobals.set_temp)
    finally:
        YafaGlobals.lock_current_settings.release()
    return '''
         <form action="/settings" method="post">
         Desired temperature: <input name="temp" type="text" value="'''+Tset+'''" style="text-align: right" onfocus="this.select();"/>
            <input value="Set" type="submit" />
         </form>
     '''

@post('/settings') # or @route('/settings', method='POST')
def do_settings():
    temp = request.forms.get('temp')
    YafaGlobals.task_q.put(temp)
    return "<p>You succesfully set the temperature to "+str(temp)+"</p>"
"""

def main():
    threads=[]
    t=threading.Thread(target=worker.main)
    t.setDaemon(True)
    threads.append(t)
    t.start();

    time.sleep(5) # quick hack to get worker going (reading settings, etc...)

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




