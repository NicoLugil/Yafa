#!/usr/bin/python

# Copyright 2014-2015 Nico Lugil <nico at lugil dot be>
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

import subprocess 
import re

def get_wifi_strength():
      p = subprocess.Popen(["iwconfig","wlan0"], stdout=subprocess.PIPE)
      out, err = p.communicate()
      m=re.search(r"Link.*dBm",out)
      if m is None:
          return "no-info"
      else:
          return m.group(0)

def get_ip():
      p = subprocess.Popen(["ifconfig","wlan0"], stdout=subprocess.PIPE)
      out, err = p.communicate()
      m=re.search(r"inet addr:([^\s]+)",out)
      if m is None:
          return "no-info"
      else:
          return m.group(1)

def getall():

    info = get_wifi_strength()
    print(info)
    info = get_ip()
    print(info)

if __name__ == '__main__':
      getall()





