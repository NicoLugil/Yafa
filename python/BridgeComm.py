import sys
import string

sys.path.insert(0, '/usr/lib/python2.7/bridge/') 
from bridgeclient import BridgeClient as bridgeclient
bc = bridgeclient()                              

class BridgeComm:
    COMMAND_LEN=16
    VALUE_LEN=32
    previous_tx_id='Z'
    def send(self,command,value):
       if BridgeComm.previous_tx_id=='Z':
          msg_id='A'
       else:
          msg_id=chr(ord(BridgeComm.previous_tx_id) + 1)
       msg=msg_id+(command[:BridgeComm.COMMAND_LEN]).ljust(BridgeComm.COMMAND_LEN)+(value[:BridgeComm.VALUE_LEN]).ljust(BridgeComm.VALUE_LEN)
       print "I123456789012345612345678901234567890123456789012"
       print "ICCCCCCCCCCCCCCCCVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
       print msg
       bc.put('key_get',msg)
       BridgeComm.previous_tx_id=msg_id




