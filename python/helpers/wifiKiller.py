#!/usr/bin/python

# turns off closes wifi periodically
# used to see how other code reacts to it

import sys    
import time
import string
import datetime
import subprocess 
import StringIO
import logging
import logging.handlers
from shutil import copyfile
import glob,os 
import re

def wifi_down_up():
      subprocess.call(["wifi","down"], stdout=open(os.devnull, 'wb'))
      time.sleep(30)
      subprocess.call("wifi", stdout=open(os.devnull, 'wb'))
      time.sleep(100)

def runit():

  while True:
      wifi_down_up()

if __name__ == '__main__':
      runit()

