#!/usr/bin/env python2
# -*- coding: utf8 -*-

# TODO:
#  * baseurl
#  * non existent attr in template
#  * UnicodeEncodeError
#  * pipe exceptions
#  * url handling


import sys
import os
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup


def show_element(elem):
    """ Output whole a element as it is. """
    return elem

def show_pair(elem):
    """ Output text and url of the link. """
    return '"%s" %s' % (elem.string, dict(elem.attrs).get('href'))

def show_url(elem):
    """ Output just url of the link. """
    return dict(elem.attrs).get('href')

def make_show(template):
    """ Generate custom show function. """
    def show_func(elem):
        attrs = dict(elem.attrs)
        attrs['text'] = elem.string
        return template % attrs
    return show_func

def process(file_obj, func):
    """ Find and process all links in file. """
    soup = BeautifulSoup(file_obj)
    for i in soup("a"):
        print func(i)

def process_file(file_path, func):
    try:
        fo = open(file_path, "r")
        process(fo, func)
        fo.close()
    except IOError, ex:
        sys.stderr.write("IO error: %s\n" % ex)

def main():
    parser = OptionParser(usage="usage: %prog [options] [files]")
    parser.set_defaults(func=show_url)
    parser.add_option("-a",
        action="store_const",
        dest="func",
        const=show_element,
        help="print whole <a> element",
        )
    parser.add_option("-p",
        action="store_const",
        dest="func",
        const=show_pair,
        help="print pair text url",
        )
    parser.add_option("-t", "--template",
        action="store",
        help="output string template, eg. '%(text)s %(href)s'",
        )
    (opts, args) = parser.parse_args()

    if opts.template is not None:
        opts.func = make_show(opts.template)
    if len(args) == 0:
        process(sys.stdin, opts.func)
        return
    for arg in args:
        process_file(arg, opts.func)

if __name__ == '__main__':
    main()
