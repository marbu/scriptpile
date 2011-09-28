#!/usr/bin/env python2.7
# -*- coding: utf8 -*-


import sys
from argparse import ArgumentParser
import ConfigParser
import shlex
import subprocess


def sync(source, target, args):
    """run rsync"""
    print "syncing '%s' to '%s'" % (source, target)
    cmd = "rsync -v -zc --archive --copy-links -e ssh %(source)s %(target)s " \
        % locals()
    if args.debug:
        print cmd
    else:
        subprocess.call(shlex.split(cmd))

def push(conf, args):
    """sync the data out"""
    sync(conf.local, conf.remote, args)

def pull(conf, args):
    """brings the data back"""
    sync(conf.remote, conf.local, args)

def info(conf, args):
    """show configuration"""
    print "local  dir: %s" % conf.local
    print "remote dir: %s" % conf.remote

def main():
    parser = ArgumentParser(description='Simple text sync tool using rsync.')
    parser.add_argument('-d',
        dest='debug',
        action='store_true',
        help='debug mode')
    subparsers = parser.add_subparsers()

    # define subcommands
    commands = {}
    for cmd in ('info', 'push', 'pull'):
        cmd_parser = subparsers.add_parser(cmd, help=globals().get(cmd).__doc__)
        cmd_parser.set_defaults(func=globals().get(cmd))
        commands[cmd] = cmd_parser

    # parse args. and conf. file
    args = parser.parse_args()
    conf = ConfigParser.RawConfigParser()
    if not conf.read('.text-sync'):
        sys.stderr.write("no text-sync directory\n")
        return 2

    # read mandatory config options
    try:
        conf.local = conf.get("dirs", "local")
        conf.remote = conf.get("dirs", "remote")
    except ConfigParser.NoOptionError, ex:
        sys.stderr.write("config file '.text-sync' : %s\n" % ex)
        return 3

    return args.func(conf, args)

if __name__ == '__main__':
    sys.exit(main())
