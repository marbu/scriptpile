#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
Simple cat implementatin in Python.
"""

import sys


def cat(fobj):
    """
    Read and print content of a file object.
    """
    for line in iter(fobj.readline, ""):
        print line,

def cat_file(filepath):
    """
    Read and print content of file by it's path.
    """
    with open(filepath, "r") as fobj:
        cat(fobj)

def main(argv=None):
    """
    Main function.
    """
    argv = argv or sys.argv
    retcode = 0
    if len(argv) == 1:
        try:
            cat(sys.stdin)
        except KeyboardInterrupt:
            print
            retcode = 130
        return retcode
    for filename in argv[1:]:
        try:
            cat_file(filename)
        except IOError, ex:
            sys.stderr.write("%s\n" % ex)
            retcode = 1
    return retcode

if __name__ == '__main__':
    sys.exit(main())
