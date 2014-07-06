#!/usr/bin/python

# Copyright 2014 Nico Lugil 
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
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.

# contact me at nico at lugil dot be 

from ftplib import FTP

def directory_exists(the_dir, ftp_object):
        filelist = []
        ftp_object.retrlines('LIST',filelist.append)
        for f in filelist:
            if f.split()[-1] == the_dir and f.upper().startswith('D'):
                   return True
        return False



