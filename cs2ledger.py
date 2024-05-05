#!/usr/bin/env python3
# -*- coding: utf8 -*-


from datetime import datetime
import argparse
import pprint
import sys
import textwrap


def seek_to(fo, exp):
    for line in fo:
        if line == exp:
            return True
    return False


def read_data(fo):
    result = []
    for line in fo:
        if len(line) > 1:
            result.append(line.strip())
        else:
            break
    return result


def cut_zero(str_val):
    if not str_val.endswith("0"):
        return str_val
    fl_val = float(str_val)
    if f"{fl_val:.2f}" == str_val[:-1]:
        return str_val[:-1]
    else:
        return str_val


class Report():

    def make_transaction(self, date, i):
        pass

    def ledger_export(self):
        transactions = []
        for i, date_raw in enumerate(self.transact_date):
            date_obj = datetime.strptime(date_raw, "%d %b %Y")
            date = date_obj.strftime("%Y-%m-%d")
            tr = self.make_transaction(date, i)
            transactions.append(tr)
        return "\n".join(transactions)

    def is_valid(self):
        exp_len = len(self.transact_date)
        result = True
        for var in vars(self).keys():
            var_len = len(getattr(self, var))
            if var_len != exp_len:
                print(f"error: {var} has {var_len} items, expected {exp_len}",
                      file=sys.stderr)
                result = False
        return result

    def dump(self):
        result = []
        for var in vars(self).keys():
            result.append(f"{var:<18}: " + str(getattr(self,var)))
        return "\n".join(result)


class ESPPReport(Report):

    header = "IBM ESPP\n"

    def __init__(self, fo):
        self.transact_date = read_data(fo)
        seek_to(fo, "Balance Forward\n")
        seek_to(fo, "\n")
        self.amount_gross_usd = read_data(fo)
        seek_to(fo, "\n")
        seek_to(fo, "\n")
        self.amount_net_usd = read_data(fo)
        seek_to(fo, "\n")
        self.fmv_atgrant_usd = read_data(fo)
        self.purchase_date = read_data(fo)
        self.fmv_atpurchase_usd = read_data(fo)
        self.per_share_usd = read_data(fo)
        self.shares = read_data(fo)
        self.shares_total = read_data(fo)
        del self.shares_total[0]

    def make_transaction(self, date, i):
        fmv_atpurchase_usd = cut_zero(self.fmv_atpurchase_usd[i])
        per_share_usd = cut_zero(self.per_share_usd[i])
        transaction = textwrap.dedent(f"""
            {date} Purchase via ESPP
                ; espp:
                ; computershare:
                assets:stocks            {self.shares[i]} IBM {{{per_share_usd} USD}} @ {fmv_atpurchase_usd} USD
                income:redhat:espp
            """)
        fee = float(self.amount_gross_usd[i]) - float(self.amount_net_usd[i])
        if fee > 0:
            transaction += f"    expenses:fees             {fee:.2f} USD\n"
        transaction += f"    assets:rht_espp_fund   -{self.amount_gross_usd[i]} USD"
        return transaction


class DSPPReport(Report):

    header = "DSPP - Common Stock\n"

    def __init__(self, fo):
        self.transact_date = read_data(fo)
        seek_to(fo, "Balance Forward\n")
        seek_to(fo, "\n")
        self.amount_gross_usd = read_data(fo)
        self.tax_withheld_usd = read_data(fo)
        self.fee_usd = read_data(fo)
        self.amount_net_usd = read_data(fo)
        self.per_share_usd = read_data(fo)
        self.shares = read_data(fo)
        self.shares_total = read_data(fo)
        del self.shares_total[0]

    def make_transaction(self, date, i):
        transaction = textwrap.dedent(f"""
            {date} Dividend
                ; dividend:
                ; computershare:
                expenses:taxes         {self.tax_withheld_usd[i]} USD
                expenses:fees          {self.fee_usd[i]} USD
                income:ibm:dividend  -{self.amount_gross_usd[i]} USD
                assets:stocks         {self.shares[i]} IBM""")
        return transaction


def extract_data(fo):
    if seek_to(fo, ESPPReport.header):
        return ESPPReport(fo)
    fo.seek(0)
    if seek_to(fo, DSPPReport.header):
        return DSPPReport(fo)
    return None


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description="ComputerShare Exporter")
    ap.add_argument(
        "file",
        nargs='+',
        type=argparse.FileType('r'),
        help="input text file")
    ap.add_argument("-d", "--debug", action="store_true", help="debug mode")
    args = ap.parse_args()

    for fo in args.file:
        # get the data from plaintext export
        report = extract_data(fo)
        if report is None:
            print(f"error: file '{fo.name}' not recognized, skipping",
                  file=sys.stderr)
            continue
        # optional debugging
        if args.debug:
            print("file:", fo.name)
            print("type:", report.header)
            print(report.dump())
        # mandatory validation
        if not report.is_valid():
            print(f"error: file '{fo.name}' is not valid, can't continue",
                  file=sys.stderr)
            sys.exit(1)
        # translating data from the report into ledger format
        print(report.ledger_export())
