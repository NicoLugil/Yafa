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

import string
import logging
import ConfigParser

class Settings:
    def __init__(self):
        #defaults when file not found
        self.name='default'
        self.temp=15.0
        self.dHeat_on=-0.5
        self.dHeat_off=0.0
        self.dCool_on=0.5
        self.dCool_off=0.0

class ParseSettings:
    def __init__(self):
        try:
            self.my_logger = logging.getLogger('MyLogger')
        except:
            # dont really know what to do in this case ... just raise for now
            # TODO
            raise
    def loadFile(self,filename,settings):
        newSettings = Settings()
        try:
            iniparser = ConfigParser.SafeConfigParser()
            iniparser.read(filename)
            newSettings.name=iniparser.get('paths','name')
            newSettings.temp=iniparser.getfloat('temps','temp')
            newSettings.dHeat_on=iniparser.getfloat('temps','dHeat_on')
            newSettings.dHeat_off=iniparser.getfloat('temps','dHeat_off')
            newSettings.dCool_on=iniparser.getfloat('temps','dCool_on')
            newSettings.dCool_off=iniparser.getfloat('temps','dCool_off')
            # when here we are ok - change values
            settings.name=newSettings.name
            settings.temp=newSettings.temp
            settings.dHeat_on=newSettings.dHeat_on
            settings.dHeat_off=newSettings.dHeat_off
            settings.dCool_on=newSettings.dCool_on
            settings.dCool_off=newSettings.dCool_off
            self.my_logger.info("settings read from "+str(filename))
        except Exception as e:
            self.my_logger.exception('Loading settings file failed - keeping old settings')
    def saveFile(self,filename,settings):
        # TODO: do this safer to avoid corrupted files (e.g. first to tmp and then rename)
        try:
            iniparser = ConfigParser.SafeConfigParser()
            iniparser.add_section('paths')
            iniparser.set('paths','name',settings.name)
            iniparser.add_section('temps')
            iniparser.set('temps','temp',str(settings.temp))
            iniparser.set('temps','dHeat_on',str(settings.dHeat_on))
            iniparser.set('temps','dHeat_off',str(settings.dHeat_off))
            iniparser.set('temps','dCool_on',str(settings.dCool_on))
            iniparser.set('temps','dCool_off',str(settings.dCool_off))
            with open(filename,'w') as inifile:
                iniparser.write(inifile)
            self.my_logger.info("New settings saved to file "+str(filename))
        except Exception as e:
            self.my_logger.exception('Saving settings file failed - these will be lost')



