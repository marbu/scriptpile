#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
Simple alarm sched script for music player daemon (MPD).

Following example:

    $ alarm.py 20:05 -d --period 20 --volume 10,50,70

will do roughly this:

    $ echo 'mpc clear; mpc load alarm; mpc play' | at 20:05
    $ echo 'mpc volume 10' | at 20:05
    $ echo 'mpc volume 50' | at 20:25
    $ echo 'mpc volume 70' | at 20:45

note: you can check the issued commands using --debug
"""


import sys
import time
from datetime import datetime, timedelta
from optparse import OptionParser
from subprocess import check_output


CMD_ALARM = "mpc clear; mpc load alarm; mpc play"
CMD_VOLUME_UP = "mpc volume %d"

def run_at(time_str, sched_cmd, debug=False):
    """
    Executes 'echo $sched_cmd | at $time'
    """
    if "'" in sched_cmd:
        raise Exception("Ops, you can't have ' char in cmd!")
    cmd = "echo '%s' | at %s" % (sched_cmd, time_str)
    output = None
    if debug:
        print cmd
    else:
        output = check_output(cmd, shell=True)
    return output

def sched_alarm(time_obj, volume_list=None, period=1, debug=False):
    """
    Schedule alarm at time given by when_str.
    """
    volume_list = volume_list or []
    # schedule alarm
    run_at(time_obj.strftime("%H:%M"), CMD_ALARM, debug)
    # gradually increase volume if required
    time_delta = timedelta(seconds=period*60)
    for volume in volume_list:
        run_at(time_obj.strftime("%H:%M"), CMD_VOLUME_UP % volume, debug)
        time_obj = time_obj + time_delta

def parse_time_spec(args):
    """
    Process args and return time object when to run the alarm.

    @param args: arg list from main
    @return    : time object (when to run the alarm)
    """
    if args[0] == "in":
        now = datetime.now()
        time_st = time.strptime(args[1], "%H:%M")
        time_delta = timedelta(hours=time_st.tm_hour, minutes=time_st.tm_min)
        time_obj = now + time_delta
    else:
        time_st = time.strptime(args[0], "%H:%M")
        time_obj = datetime(1900, 1, 1, time_st.tm_hour, time_st.tm_min, 0)
    return time_obj

def main():
    op = OptionParser(usage="usage: %prog time [options]")
    op.add_option("-d", "--debug",
        action="store_true",
        help="debug mode")
    op.add_option("-v", "--volume",
        action="store",
        type="string",
        help="volume list, eg. 5,30,70")
    op.add_option("-p", "--period",
        action="store",
        type="int",
        help="period (min) of volume ups")

    op.set_defaults(period=1)
    op.set_defaults(volume="")
    opts, args = op.parse_args()

    if len(args) > 0:
        try:
            time_obj = parse_time_spec(args)
        except Exception, ex:
            sys.stderr.write("Error: wrong time specification: %s.\n" % ex)
            return 1
    else:
        msg = "Error: time not specified (the only mandatory argument).\n"
        sys.stderr.write(msg)
        return 1

    volume_list = [int(vol) for vol in opts.volume.split(",") if vol]
    sched_alarm(time_obj, volume_list, opts.period, opts.debug)

if __name__ == '__main__':
    sys.exit(main())
