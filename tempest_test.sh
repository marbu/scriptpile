#!/bin/bash
# read /usr/share/tempest_for_eliza/README

# provided by xvidtune or xrandr
PIXELCLOCK="100000000" # times e6
HDISPLAY="1280"
VDISPLAY="800"
HTOTAL="1440"

# emmited radio frequency in Hz
RADIOFREQ=$(($1*1000))

SONGDIR="/usr/share/tempest_for_eliza/songs/"
# available songs:
# forelise fruehling godfather jonny oldmacdonald
# saints starwars tempest ungarian
SONG="${SONGDIR}forelise"

tempest_for_eliza $PIXELCLOCK $HDISPLAY $VDISPLAY $HTOTAL $RADIOFREQ $SONG
