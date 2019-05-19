#!/usr/bin/env python3
# -*- coding: utf8 -*-


import csv
import os
import subprocess
import sys


def intercept_file_option(argv):
    """
    Find and replace value of command line option for input file in given
    argv list.

    Returns tuple:
      * file_arg: the filename (value of -f option)
      * new_argv: argv with the filename replaced with "-" (if found)
    """
    file_arg = None # value of -f option in sys.argv
    file_idx = None # index of value of -f option in sys.argv

    # if the file is not specified, no change in argv is needed
    new_argv = argv

    for i, arg in enumerate(argv[1:], start=1):
        if arg != "-f":
            continue
        file_idx = i+1
        if len(argv) <= file_idx:
            # it looks like '-f' is the last option, let's not interfere
            break
        file_arg = argv[file_idx]
        new_argv = argv.copy()
        new_argv[file_idx] = "-"

    return file_arg, new_argv


def convert_csv(in_file, out_file):
    """
    Transforming csv file a bit (eg. changing delimiter, numeric format) for
    hledger to be able to read it.
    """
    csv_reader = csv.reader(in_file, delimiter=';')
    csv_writer = csv.writer(
        out_file,
        delimiter=',',
        lineterminator='\n',
        quoting=csv.QUOTE_ALL,
        )
    for row in csv_reader:
        csv_writer.writerow(row)


def main():
    file_name, argv = intercept_file_option(sys.argv)

    # let hledger handle the error message
    if file_name is None:
        cp = subprocess.run(["hledger"] + sys.argv[1:])
        return cp.returncode

    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        # child process
        os.close(r_fd)
        os.dup2(w_fd, 1)
        with open(file_name, "r", newline='') as file_obj:
            convert_csv(file_obj, sys.stdout)
        os._exit(0)
    else:
        # parent process
        os.close(w_fd)
        os.dup2(r_fd, 0)
        os.execv('/usr/bin/hledger', ['hledger'] + argv[1:])


if __name__ == '__main__':
    sys.exit(main())
