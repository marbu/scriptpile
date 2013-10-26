#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
Simple parser for czech election results site volby.cz.
"""


import sys
import re
import urllib
from optparse import OptionParser

from BeautifulSoup import BeautifulSoup


def get_soup(url):
    """
    Download page from url and parse it into soup.
    """
    page = urllib.urlopen(url)
    soup = BeautifulSoup(page)
    return soup

def extract_parties(soup):
    """
    Extract results data from soup.
    """
    parties = []
    total_votes = 0
    # get tables with results, filter rows with data
    tr_list = []
    for table in soup.findAll("table", attrs={"summary":re.compile("^Tabulk")}):
        tr_all = table.findAll("tr")
        tr_data = [tr for tr in tr_all if tr.find("td", attrs={"class":"cislo"})]
        tr_list.extend(tr_data)
    # build data structure
    for tr in tr_list:
        party = parse_tr(tr)
        parties.append(party)
        total_votes += party["vote"]
    return parties, total_votes

def parse_tr(tr_tag):
    """
    Parse tr tag into dict (with results for particular party).
    """
    td_list = tr_tag.findAll("td")
    result = {
        "id"     : td_list[0].text,
        "name"   : td_list[1].text,
        "vote"   : int(filter(lambda char: char.isdigit(), td_list[2].text)),
        "result" : float(td_list[3].text.replace(",",".")),
        }
    return result

def sort_parties(parties):
    """
    Sort list of parties by result.
    """
    cmp_func = lambda x, y: cmp(x["vote"], y["vote"])
    return sorted(parties, cmp=cmp_func, reverse=True)

def main(argv=None):
    """
    Main function.
    """
    o_parser = OptionParser(usage="usage: %prog [options] volby-cz-url")
    o_parser.add_option("-p", "--pretty",
        action="store_true",
        help="use pretty (human readable) format")
    opts, args = o_parser.parse_args()

    if len(args) > 0:
        url = args[0]
    else:
        url = "http://volby.cz/pls/ps2013/ps2?xjazyk=CZ"

    soup = get_soup(url)
    parties, total_votes = extract_parties(soup)
    parties = sort_parties(parties)

    # stats
    template = "parties: {0:d}\nvotes: {1:d}\n"
    sys.stderr.write(template.format(len(parties), total_votes))

    # result table
    if opts.pretty:
        template = u"{id:2s} : {name:30s} : {result:5.2f} : {vote:7d}"
    else:
        template = u"{id:s}:{name:s}:{result:f}:{vote:d}"
    for party in parties:
        print template.format(**party).encode("utf8")

if __name__ == '__main__':
    sys.exit(main())
