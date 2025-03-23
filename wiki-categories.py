#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Copyright 2025 Martin Bukatovič <martinb@marbu.eu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Queries to cover:
#  - tag* -> pages
#  - page* -> tags
#  - list all tags, incl. number (opt.)
#
# TODO: implement the full scope of the queries:
#  - multiple pages or categories (intersection)
#  - numbers of pages or categories for a list
#  - address code repetition in main

from collections import defaultdict
import argparse
import os
import pprint
import sys


WIKI_DIR = "/home/martin/tvorba/wiki"  # TODO: move to config file


def iterate_pages():
    """
    List all file paths of wiki pages.
    """
    for subdir, dirs, files in os.walk(WIKI_DIR):
        dirs[:] = [d for d in dirs if d not in ".git"]
        for f in files:
            if not f.endswith(".page"):
                continue
            yield os.path.join(subdir, f)


def get_categories(page):
    """
    Get list of categories for give page file object.
    """
    cat_list = []
    first_line = page.readline()
    if first_line.startswith("---"):
        while True:
            line = page.readline()
            if line.startswith("categories: "):
                cat_str = line[12:].rstrip()
                cat_list = cat_str.split(" ")
            if line.startswith("..."):
                break
    return cat_list


def build_index():
    """
    Create dict with list of page's file paths for each category.
    """
    cat_index = defaultdict(list)
    page_index = {}
    for page_path in iterate_pages():
        page_wiki_path = page_path[len(WIKI_DIR)+1:]
        with open(page_path, "r") as page_fo:
            categories = get_categories(page_fo)
            if len(categories) == 0:
                continue
            page_index[page_wiki_path] = categories
            for cat in categories:
                cat_index[cat].append(page_wiki_path)
    return cat_index, page_index


def main():
    ap = argparse.ArgumentParser(description="wiki categories helper script")
    ap.add_argument(
        "-c",
        dest="category",
        help="list pages for given categories")
    ap.add_argument(
        "-p",
        dest="page",
        help="show categories with given categories")
    ap.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="list all categories")
    ap.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="just dump index dictionaries")
    args = ap.parse_args()

    cat_index, page_index = build_index()

    if args.debug:
        pprint.pprint(cat_index)
        pprint.pprint(page_index)
        return

    if args.all:
        for cat in cat_index.keys():
            print(cat)
        return

    if args.page:
        if not args.page.endswith(".page"):
            page = args.page + ".page"
        else:
            page = args.page
        answer = page_index.get(page)
        if answer is None:
            return 1
        for cat in answer:
            print(cat)
        return

    if args.category:
        answer = cat_index.get(args.category)
        if answer is None:
            return 1
        for page in answer:
            print(page)
        return


if __name__ == '__main__':
    sys.exit(main())
