import sys
import string
import xml.etree.cElementTree as ET


# TODO
# THIS IS FAR FROM FINISHED: NO ERROR CHECKING, VERY BASIC, EXPECTS VERY SIMPLE
# XML STRUCTURE


class ParseSettings:
    name='noname'
    temp=20.0
    def parse(self):
       tree = ET.ElementTree(file='settings.xml')
       for elem in tree.iter(tag='name'):
          print elem.tag, elem.text
          self.name = elem.text
       for elem in tree.iter(tag='temp'):
          print elem.tag, elem.text
          self.temp = elem.text


