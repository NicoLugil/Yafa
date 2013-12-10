#!/usr/bin/python
import sys    
import time
import string
from BridgeComm import BridgeComm

myComm = BridgeComm()

myComm.send("boe","bah")
myComm.send("boe","bah")
myComm.send("12345678901234567","123456789012345678901234567890123")
myComm.read()

