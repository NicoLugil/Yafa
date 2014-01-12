# Author: Nico Lugil
# TODO: some more text here + some license stuff

import sys
import string
import time

class TimedActions:
   def __init__(self,interval):
        self.iv=interval;
        self.last_time=time.time()  # seconds since epoch
        self.did_run=False
   def set_interval(self,interval):
        self.iv=interval;
   def enough_time_passed(self):
        if not self.did_run:
           self.did_run=True
           self.last_time=time.time()
           return True
        else:
           if (time.time()-self.last_time)>self.iv:
              self.last_time=time.time()
              return True
           else:
              return False


