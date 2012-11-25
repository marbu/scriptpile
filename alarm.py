#!/usr/bin/env python2
# -*- coding: utf8 -*-

"""
Simple alarm sched script for music player daemon (MPD).

Following example:

    $ alarm.py -d --time 20:05 --period 20 --volume 10,50,70

will do roughly this:

    $ echo 'mpc clear; mpc load alarm; mpc play' | at 20:05
    $ echo 'mpc volume 10' | at 20:05
    $ echo 'mpc volume 50' | at 20:25
    $ echo 'mpc volume 70' | at 20:45

note: you can check the issued commands using --debug
"""


import sys
import time
import datetime
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

def sched_alarm(when_str, volume_list=None, period=1, debug=False):
    """
    Schedule alarm at time given by when_str.
    """
    volume_list = volume_list or []
    # schedule alarm
    time_st  = time.strptime(when_str, "%H:%M")
    time_obj = datetime.datetime(2012, 1, 1, time_st.tm_hour, time_st.tm_min, 0)
    run_at(time_obj.strftime("%H:%M"), CMD_ALARM, debug)
    # gradually increase volume if required
    time_delta = datetime.timedelta(seconds=period*60)
    for volume in volume_list:
        run_at(time_obj.strftime("%H:%M"), CMD_VOLUME_UP % volume, debug)
        time_obj = time_obj + time_delta

def main():
    op = OptionParser(usage="usage: %prog [options]")
    op.add_option("-t", "--time",
        action="store",
        help="when to run alarm (HH:MM)")
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

    if opts.time is not None:
        volume_list = [int(vol) for vol in opts.volume.split(",")]
        sched_alarm(opts.time, volume_list, opts.period, opts.debug)
    else:
        sys.stderr.write("Error: time not specified, use --time to set it.\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
