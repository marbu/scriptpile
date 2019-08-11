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


def make_header(pandoc_format, title):
    """
    Generate pandoc header based on given metadata.
    """
    lines = [
        "---",
        "format: " + pandoc_format,
        "categories: gititized",
        "title: " + title,
        "...",
        ]
    # separate the header from the rest of the file via empty line, with
    # exception of orgmode files ...
    if pandoc_format == "org":
        ending ="\n"
    else:
        ending ="\n\n"
    return "\n".join(lines) + ending


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
                f_out.write(make_header(pandoc_format, args.title))
                f_out.write(data)
        if args.make_commit:
            subprocess.run(["git", "rm", path])
            subprocess.run(["git", "add", new_path])
            subprocess.run(["git", "commit", "-m", "gititize " + path])
        else:
            os.remove(path)


if __name__ == '__main__':
    sys.exit(main())
