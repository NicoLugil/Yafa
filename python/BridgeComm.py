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
import time
import logging
import logging.handlers

sys.path.insert(0, '/usr/lib/python2.7/bridge/') 
from bridgeclient import BridgeClient as bridgeclient
bc = bridgeclient()                              

class BridgeComm:
    COMMAND_LEN=16
    VALUE_LEN=32
    previous_tx_id='Z'
    read_ID=''
    read_command=''
    read_value=''
    filler='#'
    def send(self,command,value):
       if BridgeComm.previous_tx_id=='Z':
          msg_id='A'
       else:
          msg_id=chr(ord(BridgeComm.previous_tx_id) + 1)
       msg=msg_id+(command[:BridgeComm.COMMAND_LEN]).ljust(BridgeComm.COMMAND_LEN,BridgeComm.filler)+(value[:BridgeComm.VALUE_LEN]).ljust(BridgeComm.VALUE_LEN,BridgeComm.filler)
       #print "I123456789012345612345678901234567890123456789012"
       #print "ICCCCCCCCCCCCCCCCVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
       #print msg
       bc.put('key_get',msg)
       time.sleep(1)   # should be replaced by handshaking TODO
       BridgeComm.previous_tx_id=msg_id
    # will return false if nothing can be read
    def check_new_msg(self):
       msg=bc.get('key_put')
       if msg is None:
          #print 'nothing\n'
          return False
       else:
          if msg[0]!=BridgeComm.read_ID: 
            #print '--',msg,'--\n'
            # remove fillers
            BridgeComm.read_ID = msg[0]
            BridgeComm.read_command = (msg[1:1+BridgeComm.COMMAND_LEN]).translate(None,BridgeComm.filler);
            BridgeComm.read_value = (msg[1+BridgeComm.COMMAND_LEN:]).translate(None,BridgeComm.filler);
            #print BridgeComm.read_ID,BridgeComm.read_command,BridgeComm.read_value
            return True
    # checks for new msg (with timeout in seconds)
    # returns true if new msg, false if timed out
    def wait_for_new_msg(self,timeout,my_logger):
         ok=False
         start=time.time();
         while True:
            if self.check_new_msg():
               ok=True
               break
            now=time.time()
            if (now-start) > timeout:
               break
            my_logger.debug("sleep")
            time.sleep(0.5)
         return ok





