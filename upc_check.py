#!/usr/bin/env python3
# -*- coding: utf8 -*-


import ipaddress
import socket
import sys

import dns.reversename
import dns.resolver


# inetnum: 213.220.224.0 - 213.220.231.255 (from whois)
ip_range = ipaddress.ip_network('213.220.224.0/21')

for ip_addr in ip_range:
    # get dns name from ip address
    rev_name = dns.reversename.from_address(str(ip_addr))
    hostname = str(dns.resolver.query(rev_name, "PTR")[0])
    # try to translate the hostname back to an ip address
    try:
        ip_addr_check = dns.resolver.query(hostname)[0]
        check_passed = str(ip_addr) == str(ip_addr_check)
    except dns.resolver.NXDOMAIN:
        ip_addr_check = "NXDOMAIN"
        check_passed = False
    # report results
    report = "{0} {1}".format(ip_addr, hostname)
    if not check_passed:
        report += " fail: {0}".format(ip_addr_check)
    print(report)
    sys.stdout.flush()
