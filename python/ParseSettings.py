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
import string
import logging
import logging.handlers
import copy

class Settings:
    def __init__(self):
        self.name='noname'
        self.temp=20.0
        self.dHeat_on=-0.2
        self.dHeat_off=0.0
        self.dCool_on=0.25
        self.dCool_off=0.1

class ParseSettings:
    def loadFile(self,filename,settings):
        newSettings = Settings()
        try:
            my_logger = logging.getLogger('MyLogger')
        except:
            # dont really know what to do in this case ... just raise for now
            # TODO
            raise
        try:
            iniparser = configparser.SafeConfigParser(inline_comment_prefixes=';')
            iniparser.read(filename)
            newSettings.name=iniparser.get('paths','name')
            newSettings.temp=iniparser.get('temps','temp')
            newSettings.dHeat_on=iniparser.get('temps','dHeat_on')
            newSettings.dHeat_off=iniparser.get('temps','dHeat_off')
            newSettings.dCool_on=iniparser.get('temps','dCool_on')
            newSettings.dCool_off=iniparser.get('temps','dCool_off')
            settings = copy.copy(newSettings)
        except Exception as e:
            my_logger.exception(e)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")

class ParseSettings:
    def __init__(self):
        self.name='noname'
        self.temp=20.0
        self.clear=False
        self.dHeat_on=-0.2
        self.dHeat_off=0.0
        self.dCool_on=0.25
        self.dCool_off=0.1
    def parse_string(self,text,my_logger):
        tree = ET.ElementTree(ET.fromstring(text))
        # TODO: more optima (no for loop for every parameter)
        for elem in tree.iter(tag='name'):
            my_logger.debug("{0} {1}".format(elem.tag,elem.text))
            self.name = elem.text
        for elem in tree.iter(tag='temp'):
            my_logger.debug("{0} {1}".format(elem.tag,elem.text))
            self.temp = elem.text
        for elem in tree.iter(tag='clear'):
            my_logger.debug("{0} {1}".format(elem.tag,elem.text))
            self.clear = str2bool(elem.text)
        for elem in tree.iter(tag='dHeat_on'):
            my_logger.debug("{0} {1}".format(elem.tag,elem.text))
            self.dHeat_on = float(elem.text)
        for elem in tree.iter(tag='dHeat_off'):
            my_logger.debug("{0} {1}".format(elem.tag,elem.text))
            self.dHeat_off = float(elem.text)
        for elem in tree.iter(tag='dCool_on'):
            my_logger.debug("{0} {1}".format(elem.tag,elem.text))
            self.dCool_on = float(elem.text)
        for elem in tree.iter(tag='dCool_off'):
            my_logger.debug("{0} {1}".format(elem.tag,elem.text))
            self.dCool_off = float(elem.text)
    def parse_file(self,filename,my_logger):
        with open (filename, "r") as myfile:
            text=myfile.read()
            self.parse_string(text,my_logger)
    def write_file(self,filename,my_logger):
        yafadoc = ET.Element('yafadoc')
        name = ET.SubElement(yafadoc,'name')
        name.text = self.name
        temp = ET.SubElement(yafadoc,'temp')
        temp.text = str(self.temp)
        clear = ET.SubElement(yafadoc,'clear')
        clear.text = 'False'
        dHeat_on = ET.SubElement(yafadoc,'dHeat_on')
        dHeat_on.text = str(self.dHeat_on)
        dHeat_off = ET.SubElement(yafadoc,'dHeat_off')
        dHeat_off.text = str(self.dHeat_off)
        dCool_on = ET.SubElement(yafadoc,'dCool_on')
        dCool_on.text = str(self.dCool_on)
        dCool_off = ET.SubElement(yafadoc,'dCool_off')
        dCool_off.text = str(self.dCool_off)
        with open (filename, "w") as myfile:
            myfile.write(ET.tostring(yafadoc))


