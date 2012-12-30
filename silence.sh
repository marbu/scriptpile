#!/bin/bash

show_help() {
  echo -e "Usage: $(basename $0) time - creates silent mp3 file\n"
  echo """Commands:
  help    this message"""
}

make_silence() {
  TIME=$1
  if [[ "$TIME" =~ ^([0-9]+)h$ ]]; then
    TIME=$((${BASH_REMATCH[1]}*3600))
  elif [[ "$TIME" =~ ^([0-9]+)m$ ]]; then
    TIME=$((${BASH_REMATCH[1]}*60))
  fi
  FILE=silence.$TIME.mp3
  $DEBUG ffmpeg \
    -ar 8000 \
    -t $TIME \
    -acodec pcm_s16le -f s16le -ac 1 -i /dev/zero \
    -acodec libmp3lame -aq 0 $FILE
}

#
# main
#

if [[ $# = 0 ]]; then
  show_help
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

case $1 in
  help) show_help;;
  *)    make_silence $1;;
esac
