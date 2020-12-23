#!/usr/bin/env python3
# -*- coding: utf8 -*-


from dataclasses import dataclass
import csv
import os
import subprocess
import sys


@dataclass
class BankCsvFormat:
    """
    Details about CSV export file format of a particular bank.
    """
    encoding: str
    csv_reader_kwargs: dict
    fields_num: int
    amounts_i: list
    unquote_i: list
    filter_data_only: bool
    def_rule_file: str


FIO = BankCsvFormat(
    encoding="utf-8",
    csv_reader_kwargs={'delimiter':';'},
    fields_num=19,
    amounts_i=[2],
    unquote_i=[],
    filter_data_only=False,
    def_rule_file="hledger-cz.fio.rules")


MBANK = BankCsvFormat(
    encoding="cp1250",
    csv_reader_kwargs={'delimiter':';', 'quotechar':'"'},
    fields_num=12,
    amounts_i=[9,10],
    unquote_i=[5],
    filter_data_only=True,
    def_rule_file="hledger-cz.mbank.rules")


def unquote(str_value):
    result = str_value
    quotechar = "'"
    if str_value.startswith(quotechar) and str_value.endswith(quotechar):
        result = str_value[1:-1].strip()
    return result


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


def convert_csv(bank, in_file, out_file):
    """
    Transforming csv file a bit (eg. changing delimiter, numeric format) for
    hledger to be able to read it.
    """
    csv_reader = csv.reader(in_file, **bank.csv_reader_kwargs)
    csv_writer = csv.writer(
        out_file,
        delimiter=',',
        lineterminator='\n',
        quoting=csv.QUOTE_ALL,
        quotechar='"',
        )
    for row in csv_reader:
        if len(row) == bank.fields_num:
            for i in bank.amounts_i:
                row[i] = row[i].replace(",", ".")
            for i in bank.unquote_i:
                row[i] = unquote(row[i])
            csv_writer.writerow(row)
        elif not bank.filter_data_only:
            # print even shorter csv lines (not representing data entries)
            csv_writer.writerow(row)


def main():
    file_name, argv = intercept_file_option(sys.argv)

    # secret wrapper debug mode (don't run hledger, just show the output)
    debug_mode = False
    if len(argv[1:]) > 1 and argv[1] == '--wd':
        del argv[1]
        debug_mode = True

    # let hledger handle the error message
    if file_name is None:
        cp = subprocess.run(["hledger"] + sys.argv[1:])
        return cp.returncode

    # try to locate rules-file
    dir_path = os.path.abspath(os.path.dirname(file_name))
    rules_file = os.path.join(dir_path, os.path.basename(file_name) + ".rules")

    # try to quess bank type from a filename
    base_name = os.path.basename(file_name)
    if "mKonto" in base_name or "eMax" in base_name or base_name.startswith("_"):
        bank = MBANK
    elif base_name.startswith("Pohyby_na_uctu"):
        bank = FIO
    else:
        err_msg = "error: failed to guess a bank type based on a filename"
        print(err_msg, file=sys.stderr)
        return 1

    # if rules file doesn't exists, try to get a default for the bank type
    if not os.path.exists(rules_file):
        here = os.path.abspath(os.path.dirname(__file__))
        rules_file = os.path.join(here, bank.def_rule_file)

    r_fd, w_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        # child process
        os.close(r_fd)
        os.dup2(w_fd, 1)
        with open(file_name, "r", encoding=bank.encoding, newline='') as f_obj:
            convert_csv(bank, f_obj, sys.stdout)
        os._exit(0)
    else:
        # parent process
        os.close(w_fd)
        os.dup2(r_fd, 0)
        hledger_args = ['hledger', '--rules-file', rules_file] + argv[1:]
        if debug_mode:
            print(" ".join(hledger_args), file=sys.stderr)
            os.execv('/usr/bin/cat', ['cat'])
        else:
            os.execv('/usr/bin/hledger', hledger_args)


if __name__ == '__main__':
    sys.exit(main())
