#!/usr/bin/env python3
# -*- coding: utf8 -*-

# randomly shows text of some free software or open source licence
# works on Fedora only

import argparse
import os
import random
import sys

LICENCES = {
    "GPLv3": "/usr/share/licenses/bash/COPYING",
    "GPLv2": "/usr/share/licenses/util-linux/COPYING.GPL-2.0-or-later",
    "ASL_2.0": "/usr/share/texlive/licenses/apache2.txt",
    "MIT": "/usr/share/licenses/libcurl/COPYING", # aka expat
    "BSD": "/usr/share/texlive/licenses/bsd.txt", # TODO: which BSD?
    }

def main():
    ap = argparse.ArgumentParser(
        description="randomly shows text of some FLOSS licence")
    ap.add_argument("-l",
        choices=list(LICENCES.keys()),
        nargs='+',
        help="show this licence(s) only")
    ap.add_argument("--check",
        action='store_true',
        help="check that licence files are available")
    args = ap.parse_args()

    if args.check:
        retcode = 0
        for name, filepath in LICENCES.items():
            if not os.path.exists(filepath):
                msg = "{0} file {1} is missing"
                print(msg.format(name, filepath), file=sys.stderr)
                retcode = 1
        return retcode

    if args.l is not None:
        if len(args.l) == 1:
            filename = LICENCES.get(args.l[0])
        else:
            license = random.choice(args.l)
            filename = LICENCES.get(license)
    else:
        filename = random.choice(list(LICENCES.values()))

    with open(filename, mode="r") as licensefile:
        print(licensefile.read())

if __name__ == '__main__':
    sys.exit(main())
