#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
Simple script parsing html pages to filter out links.
"""

# TODO:
#  * non existent attr in template
#  * UnicodeEncodeError
#  * pipe exceptions


import sys
import os
from optparse import OptionParser
from BeautifulSoup import BeautifulSoup
from urlparse import urlparse
import urllib2


def show_element(elem):
    """ Output whole a element as it is. """
    return elem

def show_pair(elem):
    """ Output text and url of the link. """
    return '"%s" %s' % (elem.string, show_url(elem))

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

def add_prefix_base(elem, base_url):
    """ Add base url prefix to achnor element. """
    attrs = dict(elem.attrs)
    href= attrs.get("href")
    if href is None:
        return elem
    url = urlparse(href)
    if url.scheme != "" or url.netloc != "":
        return elem
    if href.startswith("/"):
        template = "%s%s"
    else:
        template = "%s/%s"
    attrs["href"] = template % (base_url, href)
    elem.attrs = [tuple([x, y]) for x, y in attrs.iteritems()]
    return elem

def process(file_obj, opts, base_url):
    """ Find and process all links in file. """
    soup = BeautifulSoup(file_obj)
    for el in soup("a"):
        if base_url:
            el = add_prefix_base(el, base_url)
        print opts.func(el)

def process_file(file_path, opts):
    url = urlparse(file_path)
    base_url = opts.base_url
    try:
        if url.scheme == '':
            fo = open(file_path, "r")
        elif url.scheme == 'file':
            file_path = "/".join(filter(lambda x: x, [url.netloc, url.path]))
            fo = open(file_path, "r")
        else:
            fo = urllib2.urlopen(file_path)
            if opts.link_conv and base_url is None:
                base_url = "%s://%s%s" % (url.scheme, url.netloc, url.path)
        process(fo, opts, base_url)
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
    parser.add_option("--template",
        action="store",
        help="output string template, eg. '%(text)s %(href)s'",
        )
    parser.add_option("-k", "--convert-links",
        action="store_true",
        dest="link_conv",
        help="convert relative links to absolute",
        )
    parser.add_option("--base-url",
        action="store",
        help="set base url manually",
        )
    (opts, args) = parser.parse_args()

    if opts.template is not None:
        opts.func = make_show(opts.template)
    if len(args) == 0:
        process(sys.stdin, opts)
        return
    for arg in args:
        process_file(arg, opts)

if __name__ == '__main__':
    main()
