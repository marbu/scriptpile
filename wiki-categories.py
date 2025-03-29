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
        with open(page_path, "r", encoding="utf-8") as page_fo:
            categories = get_categories(page_fo)
            if len(categories) == 0:
                continue
            page_index[page_wiki_path] = categories
            for cat in categories:
                cat_index[cat].append(page_wiki_path)
    return cat_index, page_index


def query_index(query_item, index, page_mode):
    """
    Query the index for given query item.
    """
    if page_mode:
        if not query_item.endswith(".page"):
            query_item = query_item + ".page"
    items = index.get(query_item)
    return items


def compute_answer(query_list, index, page_mode, intersect_mode):
    """
    Compute the answer for a query (list of categories or pages).
    """
    answer = []
    # initialize answer for intersection mode
    if intersect_mode:
        answer = query_index(query_list[0], index, page_mode)
    # update the the answer for each item in the query list
    for query_item in query_list:
        items = query_index(query_item, index, page_mode)
        if items is None:
            if intersect_mode:
                return []
            else:
                continue
        if intersect_mode:
            answer = [i for i in answer if i in items]
        else:
            answer.extend(items)
    return answer


def main():
    ap = argparse.ArgumentParser(
        description="wiki-categories: list pages for given categories and vice versa")
    ap.add_argument(
        dest="categories",
        nargs="*",
        help="list of categories")
    ap.add_argument(
        "-p",
        dest="pages",
        action='store_true',
        help="inverse mode (list categories for given pages instead)")
    ap.add_argument(
        "-i",
        "--intersect",
        action="store_true",
        help="use intersection to get answer for multiple categories/pages")
    ap.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="list all categories")
    ap.add_argument(
        "-s",
        "--sort",
        action="store_true",
        help="sort result by number of pages/categories if possible")
    ap.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="dump index dictionaries and exit")
    args = ap.parse_args()

    cat_index, page_index = build_index()

    # debugging mode
    if args.debug:
        pprint.pprint(cat_index)
        pprint.pprint(page_index)
        return 0

    # listing mode
    if args.list:
        if args.sort:
            for cat, pages in sorted(cat_index.items(), key=lambda i: len(i[1]), reverse=True):
                num = len(pages)
                print(f"{num}\t{cat}")
        else:
            for cat in cat_index.keys():
                print(cat)
        return 0

    # select which index to use
    if args.pages:
        index = page_index
    else:
        index = cat_index

    # get and print answer for the query
    answer = compute_answer(args.categories, index, args.pages, args.intersect)
    if len(answer) == 0:
        return 1
    for item in answer:
        print(item)
    return 0


if __name__ == '__main__':
    sys.exit(main())
