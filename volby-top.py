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
    return parties

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

def add_stats(parties, template, pretty=False):
    """
    Compute and append additional data from the results.
    """
    total_vote = 0
    total_effective_vote = 0
    for party in parties:
        total_vote += party["vote"]
        if party["result"] >= 5:
            total_effective_vote += party["vote"]
    # print total vote stats
    effective_percentage = 100/float(total_vote)*total_effective_vote
    effective_template = "votes: {0:d}\neffective votes: {1:d} ({2:5.2f}%)\n"
    sys.stderr.write(effective_template.format(
        total_vote,
        total_effective_vote,
        effective_percentage))
    # compute percentage with respect to effective votes
    for party in parties:
        if party["result"] >= 5:
            percentage_effective = party["vote"]*100/float(total_effective_vote)
        else:
            percentage_effective = 0
        party["effective"] = percentage_effective
    if pretty:
        template += " : {effective:5.2f}"
    else:
        template += ":{effective:f}"
    return parties, template

def main(argv=None):
    """
    Main function.
    """
    o_parser = OptionParser(usage="usage: %prog [options] volby-cz-url")
    o_parser.add_option("-p", "--pretty",
        action="store_true",
        help="use pretty (human readable) format")
    o_parser.add_option("-s", "--stats",
        action="store_true",
        help="show additional stats")
    opts, args = o_parser.parse_args()

    if len(args) > 0:
        url = args[0]
    else:
        url = "http://volby.cz/pls/ps2013/ps2?xjazyk=CZ"

    soup = get_soup(url)
    parties = extract_parties(soup)
    parties = sort_parties(parties)

    # stats
    template = "parties: {0:d}\n"
    sys.stderr.write(template.format(len(parties)))

    # result table
    if opts.pretty:
        template = u"{id:2s} : {name:30s} : {result:5.2f} : {vote:7d}"
    else:
        template = u"{id:s}:{name:s}:{result:f}:{vote:d}"
    if opts.stats:
        parties, template = add_stats(parties, template, opts.pretty)
    for party in parties:
        print template.format(**party).encode("utf8")

if __name__ == '__main__':
    sys.exit(main())
