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
import xml.etree.cElementTree as ET
import logging
import logging.handlers

# TODO
# THIS IS FAR FROM FINISHED: NO ERROR CHECKING, VERY BASIC, EXPECTS VERY SIMPLE
# XML STRUCTURE

def str2bool(v):
      return v.lower() in ("yes", "true", "t", "1")

class ParseSettings:
    name='noname'
    temp=20.0
    clear=False
    def parse_string(self,text,my_logger):
       tree = ET.ElementTree(ET.fromstring(text))
       for elem in tree.iter(tag='name'):
          my_logger.debug("{0} {1}".format(elem.tag,elem.text))
          self.name = elem.text
       for elem in tree.iter(tag='temp'):
          my_logger.debug("{0} {1}".format(elem.tag,elem.text))
          self.temp = elem.text
       for elem in tree.iter(tag='clear'):
          my_logger.debug("{0} {1}".format(elem.tag,elem.text))
          self.clear = str2bool(elem.text)
    def parse_file(self,filename,my_logger):
        with open (filename, "r") as myfile:
                text=myfile.read()
                parse_string(text,my_logger)





