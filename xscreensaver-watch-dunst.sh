#!/bin/bash

# What the heck is this? A hack addressing a little annoying problem as
# reported in https://github.com/dunst-project/dunst/issues/77
# by https://github.com/qsuscs
# via https://github.com/dunst-project/dunst/issues/77#issuecomment-418526681
#
# See also:
# * https://github.com/dunst-project/dunst/issues/77#issuecomment-11372069
# * https://www.jwz.org/xscreensaver/faq.html#popup-windows

# Report an error if anything fails. Just in case.
set -e

xscreensaver-command -watch | while read EVENT _; do
  case "${EVENT}" in
    LOCK|BLANK) pkill -USR1 -x -u ${UID} dunst;;
    UNBLANK)    pkill -USR2 -x -u ${UID} dunst;;
  esac
done

# This script is expected to be always running, so let's return non zero code
# so that systemd can restart this script if it ever happen to stop for some
# reason.
exit 1
