#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
wiki-export-split: split wikipedia xml dump into plain text files
"""

# Copyright (C) 2014 martin.bukatovic@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import sys
import xml.sax
from optparse import OptionParser
from tempfile import NamedTemporaryFile


class WikiPageDumper(object):
    """
    Wiki page file dumper.
    """

    def __init__(self, ignore_redirect=False):
        self.id = None
        self.title = None
        self._file = None
        self._ignore_redirect = ignore_redirect

    def start(self):
        self.id = None
        self.title = None
        self._file = NamedTemporaryFile(suffix=".wikitext", dir=os.getcwd(), delete=False)

    def write(self, content):
        if self._ignore_redirect and content.startswith('#REDIRECT'):
            os.unlink(self._file.name)
        else:
            self._file.write(content.encode("utf8"))

    def end(self):
        self._file.close()


class WikiPageHandler(xml.sax.ContentHandler):
    """
    Page extracting SAX handler.
    Expected input: pages-articles.xml file (full xml dump of wikipedia pages)
    """

    # See Wikipedia pages:
    # https://meta.wikimedia.org/wiki/Help:Export#Export_format
    # https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles.xml.bz2

    def __init__(self, page_dumper):
        xml.sax.ContentHandler.__init__(self)
        self._inside_page = False
        self._curr_elem = None
        self.page = page_dumper

    def startElement(self, name, attrs):
        if name == "page":
            self._inside_page = True
            self.page.start()
            return
        if not self._inside_page:
            return
        self._curr_elem = name

    def endElement(self, name):
        if name == "page":
            self._inside_page = False
            self.page.end()
        self._curr_elem = None

    def characters(self, content):
        if not self._inside_page:
            return
        if self._curr_elem == "id":
            self.page.id = content
        elif self._curr_elem == "title":
            self.page.title = content
        elif self._curr_elem == "text":
            self.page.write(content)


def process_xml(xml_file, opts):
    """
    Process xml file with wikipedia dump.
    """
    parser = xml.sax.make_parser()
    page_dumper = WikiPageDumper(ignore_redirect=opts.noredir)
    parser.setContentHandler(WikiPageHandler(page_dumper))
    parser.parse(xml_file)

def main(argv=None):
    op = OptionParser(usage="usage: %prog [options] [wikixml]")
    op.add_option("--noredir", action="store_true", help="ignore redirection pages")
    opts, args = op.parse_args()

    if len(args) == 0:
        process_xml(sys.stdin, opts)
    else:
        with open(args[0], "r") as fobj:
            process_xml(fobj, opts)

if __name__ == '__main__':
    sys.exit(main())
