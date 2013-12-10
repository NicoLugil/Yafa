#!/usr/bin/python
import sys    
import time
import string
from BridgeComm import BridgeComm

myComm = BridgeComm()

myComm.send("boe","bah")

