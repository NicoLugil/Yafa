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

from bottle import run, route, get, post, request, template, TEMPLATE_PATH, TEMPLATES, static_file, redirect
import threading
import time
import copy

import YafaGlobals
import worker

my_error_message = "Oops something went wrong!"
full_wait_time = YafaGlobals.timeleft

# TODO: debug mode off?

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./views/')

@route('/')
def root():
    # TODO: timeout ?
    try:
        YafaGlobals.lock_temperature.acquire()
        temp_copy=copy.copy(YafaGlobals.temperature)
    except:
        return my_error_message+' : copy temperature'
    finally:
        YafaGlobals.lock_temperature.release()
    try:
        YafaGlobals.main_lock.acquire()
        settings_copy=copy.copy(YafaGlobals.settings)
        mode_copy=copy.copy(YafaGlobals.mode)
        timeleft_copy=copy.copy(YafaGlobals.timeleft)
    except:
        return my_error_message+' : copy settings'
    finally:
        YafaGlobals.main_lock.release()
    perc_rem=int(100.0*timeleft_copy/full_wait_time)
    return template('root',
                   name=settings_copy.name,
                   temp=settings_copy.temp,
                   dHeat_on=settings_copy.dHeat_on,
                   dHeat_off=settings_copy.dHeat_off,
                   dCool_on=settings_copy.dCool_on,
                   dCool_off=settings_copy.dCool_off,
                   mode=mode_copy,
                   temp_meas=temp_copy,
                   perc_rem=perc_rem)

@get('/settings')
def settings():
    try:
        YafaGlobals.main_lock.acquire()
        settings_copy=copy.copy(YafaGlobals.settings)
    except:
        return my_error_message+' : copy settings'
    finally:
        YafaGlobals.main_lock.release()
    return template('settings',
                   name=settings_copy.name,
                   temp=settings_copy.temp,
                   dHeat_on=settings_copy.dHeat_on,
                   dHeat_off=settings_copy.dHeat_off,
                   dCool_on=settings_copy.dCool_on,
                   dCool_off=settings_copy.dCool_off)

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
    redirect("/")

def main():


    # start worker
    threads=[]
    t=threading.Thread(target=worker.main)
    t.setDaemon(True)
    threads.append(t)
    t.start();
    time.sleep(5) # quick 'hack' to get worker going (reading settings, etc...)

    TEMPLATES.clear()
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




