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
          msg_id=chr(ord(previous_tx_id) + 1)
          msg=msg_id+(command[:COMMAND_LEN]).ljust(COMMAND_LEN)+(value[:VALUE_LEN]).ljust(VALUE_LEN)
          bc.put('key_get',msg)
       BridgeComm.previous_tx_id=msg_id




