#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import sys
import xml.etree.cElementTree as ET


def xml_data_pp(fo, ids=" "):
    """
    Pretty print given data oriented xml (passed via `fo` file object).
    """
    # event based element tree
    itree = ET.iterparse(fo, events=("start", "end"))
    # current indentation level (depth of current element in xml tree)
    level = 0

    for event, el in itree:
        if event == "start":
            print(ids*level + "<" + el.tag, end='')
            level += 1
            if len(el.attrib) > 0:
                print()
                for name in sorted(el.attrib):
                    templ = '{0}{1}="{2}"'
                    print(templ.format(ids*level, name, el.attrib[name]))
                print(ids*level + ">")
            else:
                print(">")
        elif event == "end":
            level -= 1
            print(ids*level + "</" + el.tag + ">")
        # we no longer need to keep data of this element in the memory
        el.clear()


def main():
    ap = argparse.ArgumentParser(
        description="Reformat data oriented xml document")
    ap.add_argument(
        "file",
        nargs='?',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="input xml file")
    ap.add_argument(
        "-i",
        default="  ",
        help="indentation string, 2 spaces is the default")
    args = ap.parse_args()

    # minimal xml prolog
    print('<?xml version="1.0" encoding="UTF-8"?>')

    xml_data_pp(args.file, ids=args.i)


if __name__ == '__main__':
    sys.exit(main())
