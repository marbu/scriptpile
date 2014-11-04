#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
xml-sax-gen: example of SAX based generation of xml file

Inspired by http://www.xml.com/pub/a/2003/03/12/py-xml.html

This is just a simple example how to create xml file when you:

 * need to do it by gradually appending new elements
 * without holding the whole xml in memory

Please take a note: *actually* logging in xml format is *terrible idea*.
"""

import random
import sys
import time
from xml.sax.saxutils import XMLGenerator
from xml.sax.xmlreader import AttributesImpl


class XmlLogger(object):
    """
    Simple&stupid XML logger based on SAX XMLGenerator.
    """

    def __init__(self, output):
        self._xmlgen = XMLGenerator(output, "utf-8")
        self._xmlgen.startDocument()
        self._xmlgen.startElement('log', AttributesImpl({}))
        self._xmlgen.characters('\n')

    def log(self, level, msg):
        now = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
        attr_vals = {'date': now, 'level': level}
        self._xmlgen.startElement('entry', AttributesImpl(attr_vals))
        self._xmlgen.characters(msg)
        self._xmlgen.endElement('entry')
        self._xmlgen.characters('\n')

    def close(self):
        self._xmlgen.endElement('log')
        self._xmlgen.characters('\n')
        self._xmlgen.endDocument()


def main():
    xml = XmlLogger(sys.stdout)
    # let's demonstrate that it actually works: generate quite long document
    for i in xrange(10000):
        log_level = random.choice(("info", "warn", "fail"))
        xml.log(log_level, "%04d" % i)
    xml.close()

if __name__ == '__main__':
    sys.exit(main())
