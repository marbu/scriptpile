#!/usr/bin/env python2.7
# -*- coding: utf8 -*-

"""
Simple shell wrapper syncing 'text directories' with rsync.
Where 'text directory' contains only big, binary and hardly
changed data (images, pdf files, ...).
"""

CONF_TEMPLATE = """[dirs]
local = %(local)s/
remote = %(remote)s
"""

# TODO:
# add cmd abritriary arg. handling for rsync
# add man config spec
# add logging
# add support for symlinked dirs
# add support for multiple targets,
#     rename 'dirs' in conf. to 'default'


import sys
import os
from argparse import ArgumentParser
import ConfigParser
import shlex
import subprocess


def sync(source, target, args):
    """run rsync"""
    print "syncing '%s' to '%s'" % (source, target)
    cmd = ("rsync"
        " --verbose"
        " --compress"
        " --progress"
        " --checksum"
        " --archive"
        " --copy-links"
        " -e ssh %(source)s %(target)s"
        ) % locals()
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

def init(args):
    """create configuration"""
    content = CONF_TEMPLATE % {"local": args.text_dir, "remote":""}
    if args.debug:
        print content
        return
    try:
        fd = os.open(".text-sync", os.O_WRONLY|os.O_CREAT|os.O_EXCL)
    except OSError:
        sys.stderr.write("config file '.text-sync' already exists\n")
        return 1
    os.write(fd, content)
    os.close(fd)

def main():
    parser = ArgumentParser(description='Simple text sync tool using rsync.')
    parser.add_argument('-d',
        dest='debug',
        action='store_true',
        help='debug mode')
    subparsers = parser.add_subparsers()

    # define subcommands
    commands = {}
    for cmd in ('init', 'info', 'push', 'pull'):
        cmd_parser = subparsers.add_parser(cmd, help=globals().get(cmd).__doc__)
        cmd_parser.set_defaults(func=globals().get(cmd))
        commands[cmd] = cmd_parser
    commands['init'].add_argument('text_dir', help='directory with text repo')

    args = parser.parse_args()

    # init hack
    if args.func.__name__ == 'init':
        return args.func(args)

    # parse conf. file
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
