#!/usr/bin/env python3
# -*- coding: utf8 -*-

# Copyright 2025 Martin Bukatovič <martinb@marbu.eu>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from datetime import datetime, timedelta
import argparse
import os
import pathlib
import subprocess
import sys


SYNTAX_TYPES = ["md", "org", "rst"]
SCREENSHOT_DIR = "/home/martin/tvorba/screenshots"  # TODO: move to config file


def get_screenshot_filename():
    """
    Generate file name for a new screenshot following spectacle naming scheme.
    """
    now = datetime.now()
    name = "Screenshot_" + now.strftime("%Y%m%d_%H%M%S") + ".png"
    path = os.path.join(SCREENSHOT_DIR, name)
    return path


def take_screenshot():
    """
    Run spectacle (KDE Screenshot Utility) to take a screenshot with given
    file name.
    """
    file_path = get_screenshot_filename()
    # TODO: spectacle fails to capture the target window properly if executed
    # this way, wtf?
    subprocess.call([
        "spectacle",
        "--windowundercursor",
        "--onclick",
        "--delay", "1000",
        "--output", file_path])
    return file_path


def parse_timestamp(timestamp_str):
    """
    Parse timestamp string into datetime object. Assume just time or full date
    timestamps.
    """
    if len(timestamp_str) <= 5:
        t = datetime.strptime(timestamp_str, "%H:%M").time()
        d = datetime.now()
        dt = datetime.combine(d, t)
    else:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M")
    return dt


def find_screenshots(s_ts, num, time_window):
    """
    Return list with file names of existing excreenshots based on given
    parameters:
     - Start with the last screenshot or with the first screenshot after
       given "since" timestamp.
     - In both cases (start with the latest one or with the one after since
       timestamp) number of retunred screenhosts depends on given number or
       a time window. The time window takes prefference over the number.
     - So one can ask for either 10 latest screenshots, or 10 screenshots after
       given timestamp.
     - Or ask for screenshots taken within last 10 minutes, or within 10
       minutes after given timestamp.
    """
    path_gen = pathlib.Path(SCREENSHOT_DIR).glob("*.png")
    screenshots = []
    if time_window is not None:
        window_td = timedelta(minutes=time_window)
    # when a start/since timestamp is defined
    if s_ts is not None:
        # TODO: this is hardly optimal approach, as we are issuing stat systall
        # twice for every file, but hey, it works kind of well at first try ...
        for path in sorted(path_gen, key=os.path.getmtime, reverse=False):
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if mtime < s_ts:
                continue
            if time_window is not None and mtime - s_ts > window_td:
                break
            if time_window is None and len(screenshots) >= num:
                break
            screenshots.append(os.path.basename(path))
        return screenshots
    # without a start/since timestamp, we start with the latest screenshot
    s_ts = datetime.now()
    for path in sorted(path_gen, key=os.path.getmtime, reverse=True):
        # TODO: the same problem with efficiency and stat calls again
        mtime = datetime.fromtimestamp(path.stat().st_mtime)
        if time_window is not None and s_ts - mtime > window_td:
            break
        if time_window is None and len(screenshots) >= num:
            break
        screenshots.append(os.path.basename(path))
    return screenshots


def main():
    ap = argparse.ArgumentParser(
        description="take or find a screesnhot and show link code for it")
    ap.add_argument(
        "-l",
        "--last",
        action="store_true",
        help="don't take new screenshot, use the last one")
    ap.add_argument(
        "--since",
        metavar="TIMESTAMP",
        help="don't take new screenshot, use screenshot(s) since given moment")
    ap.add_argument(
        "-n",
        type=int,
        metavar="N",
        default=1,
        help="number of existing screenshots to use")
    ap.add_argument(
        "-w",
        "--window",
        type=int,
        metavar="MIN",
        help="use screenshots within given time window (in minutes)")
    ap.add_argument(
        "-s",
        dest="syntax",
        choices=SYNTAX_TYPES,
        default="md",
        help="link syntax, md (markdown) is used if not specified")
    ap.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="dry run, don't take new screnshot nor wiki-link it")
    args = ap.parse_args()

    if not args.last and args.since is None:
        path = take_screenshot()
        if not os.path.exists(path):
            print("screenshot not saved")
            return
        if args.dry_run:
            print(path)
        else:
            subprocess.call(["wiki-link", "-s", args.syntax, path])
        return

    ts = args.since
    if args.since is not None:
        try:
            ts = parse_timestamp(args.since)
        except ValueError as ex:
            print("error: invalid since timestamp:", ex, file=sys.stderr)
            return 1

    for name in find_screenshots(ts, args.n, args.window):
        path = os.path.join(SCREENSHOT_DIR, name)
        if args.dry_run:
            print(path)
        else:
            subprocess.call(["wiki-link", "-s", args.syntax, path])


if __name__ == '__main__':
    sys.exit(main())
