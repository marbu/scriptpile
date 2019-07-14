#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import os
import os.path
import sys


def main():
    ap = argparse.ArgumentParser(
        description="delete extraneous files with given suffix",
        )
    ap.add_argument("dir", help="directory to process")
    ap.add_argument(
        "-e",
        "--extension",
        required=True,
        help="file extension of extraneous files to be deleted")
    ap.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="dry run, only shows which files would be deleted")
    args = ap.parse_args()

    for root, dirs, files in os.walk(args.dir):
        file_dict = {}
        for filename in files:
            fn_root, fn_ext = os.path.splitext(filename)
            file_dict.setdefault(fn_root, []).append(fn_ext)
        for fn_root, fn_ext_list in file_dict.items():
            if len(fn_ext_list) > 1 and args.extension in fn_ext_list:
                full_path = os.path.join(root, fn_root + args.extension)
                if args.dry_run:
                    print(full_path)
                else:
                    os.remove(full_path)


if __name__ == '__main__':
    sys.exit(main())
