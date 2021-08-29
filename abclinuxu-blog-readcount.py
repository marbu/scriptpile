#!/usr/bin/env python3
# -*- coding: utf8 -*-

import argparse
import sys

import lxml.html


def get_meta(meta_str):
    """
    Get metadata from meta-vypis string.
    """
    meta_list = [i.strip() for i in meta_str.split("|")]
    timestamp = meta_list[0]
    read_count = 0
    comments = 0
    for item in meta_list:
        if "Přečteno" in item:
            read_count = int(item[10:-1])
        if "Komentářů" in item:
            count, last = item.split(",")
            comments = int(count[11:])
    return timestamp, read_count, comments


ap = argparse.ArgumentParser(description="abclinuxu.cz blog read counter")
ap.add_argument(
    "file",
    nargs='*',
    type=argparse.FileType('r'),
    default=[sys.stdin],
    help="input html file with blog overview")
ap.add_argument("-t", action='store_true', help="show time stamp")
ap.add_argument("-r", action='store_true', help="show read count")
ap.add_argument("-c", action='store_true', help="show comment count")
args = ap.parse_args()


for fo in args.file:
    html = lxml.html.fromstring(fo.read())
    for post_div in html.xpath("//div[@class='cl']"):
        post_path = post_div.xpath("./h2/a/@href")[0]
        meta_p = post_div.xpath("./p[@class='meta-vypis']")[0]
        ts, read_count, comments = get_meta(meta_p.text_content())
        print(post_path, end=" ")
        if args.t:
            print(ts, end=" ")
        if args.r:
            print(read_count, end=" ")
        if args.c:
            print(comments, end=" ")
        print()
