#!/usr/bin/env python3
# -*- coding: utf8 -*-


import argparse
import os.path
import sys


def parse_line(line_str):
    """
    Parse a line from sha1sum output into tuple of hash, directory path and
    file name.

    Eg. line '3af30443352a5760cb0f88e619819cee1b1599e0 foo/bar/baz' would
    be parsed into tuple
    ('3af30443352a5760cb0f88e619819cee1b1599e0', 'foo/bar', 'baz').
    """
    line_str = line_str.rstrip()
    hash_str, path_str = line_str.split(' ', maxsplit=1)
    path_pair = os.path.split(path_str)
    return hash_str, path_pair[0], path_pair[1]


def make_rel_path(path, basedir):
    """
    If a basedir is specified, ignore everything outside of it and drop the
    basedir prefix from a file path.
    """
    if basedir is not None:
        if basedir == os.path.commonpath([basedir, path]):
            return path[len(basedir) + 1:]
        else:
            return None
    else:
        return path


def build_dir_dict(fo, basedir):
    """
    Build a dict structure so that there is a key for every (non empty)
    dictionary with another dict as a value, which translates filename into
    sha1 hash of all files of the dictionary.

    Eg. for file 'foo/bar/baz' with sha1 hash
    '3af30443352a5760cb0f88e619819cee1b1599e0', the structure would look like:
    dir_dict['foo/bar'] = {'baz': '3af30443352a5760cb0f88e619819cee1b1599e0'}
    """
    dir_dict = {}
    for line in fo:
        hs, ds, fs = parse_line(line)
        ds = make_rel_path(ds, basedir)
        if ds is None:
            continue
        dir_dict.setdefault(ds, {})[fs] = hs
    return dir_dict


def dirdiff(fo1, fo2, basedir1=None, basedir2=None):
    """
    Compare directory trees based on 2 hash files (fo1 and fo2).

    Outputs:
    * D1 when given directory exists only in hashfile1
    * D2 when given directory exists only in hashfile2
    * F1 when given file exists only in hashfile1
    * F2 when given file exists only in hashfile2
    * FD when given file exists in both, but the content differs
    """
    dd1 = build_dir_dict(fo1, basedir1)
    dd2 = build_dir_dict(fo2, basedir2)
    for dir_path in dd1:
        if dir_path not in dd2:
            print('D1 {}'.format(dir_path))
        else:
            for file_name in dd1[dir_path]:
                if file_name not in dd2[dir_path]:
                    print('F1 {}/{}'.format(dir_path, file_name))
                elif dd1[dir_path][file_name] != dd2[dir_path][file_name]:
                    print('FD {}/{}'.format(dir_path, file_name))
            for file_name in dd2[dir_path]:
                if file_name not in dd1[dir_path]:
                    print('F2 {}/{}'.format(dir_path, file_name))
    for dir_path in dd2:
        if dir_path not in dd1:
            print('D2 {}'.format(dir_path))


def main():
    ap = argparse.ArgumentParser(description="dir diff script")
    ap.add_argument("hashfile1", help="checksum file #1")
    ap.add_argument("hashfile2", help="checksum file #2")
    ap.add_argument("--basedir1", required=False, help="basedir for hashfile1")
    ap.add_argument("--basedir2", required=False, help="basedir for hashfile2")
    args = ap.parse_args()

    with open(args.hashfile1, "r", encoding='utf-8') as fo1, \
         open(args.hashfile2, "r", encoding='utf-8') as fo2:
        dirdiff(fo1, fo2, basedir1=args.basedir1, basedir2=args.basedir2)


if __name__ == '__main__':
    sys.exit(main())
