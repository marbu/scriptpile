#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import os
import subprocess
import sys


# based on `pandoc --list-input-formats`
PANDOC_FORMATS = [
    "commonmark",
    "creole",
    "docbook",
    "gfm",
    "haddock",
    "html",
    "jats",
    "json",
    "latex",
    "markdown",
    "markdown_github",
    "markdown_mmd",
    "markdown_phpextra",
    "markdown_strict",
    "mediawiki",
    "muse",
    "native",
    "opml",
    "org",
    "rst",
    "t2t",
    "textile",
    "tikiwiki",
    "twiki",
    "vimwiki",
    ]


EXT2FORMAT = {
    ".md": "markdown",
    ".tex": "latex",
    }


def ext2format(ext, default):
    """
    Get pandoc format based on file extension. Returns none if ext is not
    recognized.
    """
    if len(ext) == 0:
        pandoc_format = default
    elif ext[1:] in PANDOC_FORMATS:
        pandoc_format = ext[1:]
    else:
        pandoc_format = EXT2FORMAT.get(ext)
    return pandoc_format


def get_categories(cat_str):
    """
    Transform string with categories from cli into list of categories.
    """
    if cat_str is None:
        cat_list = ['gititized']
    elif len(cat_str) == 0 :
        cat_list = []
    else:
        cat_list = cat_str.split(',')
    return cat_list


def make_header(pandoc_format, title, categories):
    """
    Generate pandoc header based on given metadata.
    """
    lines = [
        "---",
        "format: " + pandoc_format,
        "title: " + title,
        "...",
        ]
    if categories is not None and len(categories) > 0:
        lines.insert(2, "categories: " + " ".join(categories))
    # separate the header from the rest of the file via empty line, with
    # exception of orgmode files ...
    if pandoc_format == "org":
        ending ="\n"
    else:
        ending ="\n\n"
    return "\n".join(lines) + ending


def format_md_links(data):
    """
    Find url strings and convert them into valid markdown links
    assuming there are no spaces in an url.
    """
    lines = data.splitlines()
    for i, line in enumerate(lines):
        words = line.split()
        line_changed = False
        for j, word in enumerate(words):
            if word.startswith("http"):
                words[j] = "<" + word + ">"
                line_changed = True
        if line_changed:
            # convert the line to a list item if there is nothing else there
            if len(words) == 1:
                words.insert(0, "*")
            lines[i] = " ".join(words)
    return '\n'.join(lines) + '\n'


def main():
    ap = argparse.ArgumentParser(
        description="Convert given text file into gitit wikipage file.")
    ap.add_argument(
        "file",
        nargs='+',
        help="input text file to convert")
    ap.add_argument("-f",
        dest="use_force",
        action="store_true",
        help="force conversion for a file without extension")
    ap.add_argument("-c",
        dest="make_commit",
        action="store_true",
        help="make a git commit for the conversion")
    ap.add_argument("-d",
        dest="default_format",
        default="markdown",
        help=("pandoc format for files without extension "
              "(markdown used if this option is not specified)"))
    ap.add_argument("-t",
        dest="title",
        default="TODO",
        help="title of the wikipage")
    ap.add_argument("-l",
        dest="labels",
        help="list of labels (wikipage categories) separated by a comma")
    args = ap.parse_args()

    for path in args.file:
        root, ext = os.path.splitext(path)
        if len(ext) <= 1 and not args.use_force:
            print("skipping " + path + " (no extension)", file=sys.stderr)
            continue
        pandoc_format = ext2format(ext, args.default_format)
        if pandoc_format is None:
            print("skipping " + path + " (unknown format)", file=sys.stderr)
            continue
        new_path = root + ".page"
        with open(path, "r") as f_in:
            data = f_in.read()
            with open(new_path, "w") as f_out:
                categories = get_categories(args.labels)
                header = make_header(pandoc_format, args.title, categories)
                f_out.write(header)
                if pandoc_format.startswith("markdown"):
                    data = format_md_links(data)
                f_out.write(data)
        if args.make_commit:
            subprocess.run(["git", "rm", path])
            subprocess.run(["git", "add", new_path])
            subprocess.run(["git", "commit", "-m", "gititize " + path])
        else:
            os.remove(path)


if __name__ == '__main__':
    sys.exit(main())
