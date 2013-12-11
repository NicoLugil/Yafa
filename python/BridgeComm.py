import sys
import string
import time

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
            print BridgeComm.read_ID,BridgeComm.read_command,BridgeComm.read_value
            return True






