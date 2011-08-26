#!/bin/bash
# marbu, 2011

SPEED=1.8
VOLUME=25dB
WDIR=/dev/shm

show_help() {
  echo -e "Usage: make-faster-louder.sh audio files\n"
}

# todo: do it on the stream, not secure :(

make_loud()
{
  FILE=$1
  NAME=${1%.avi}
  SHMD=${WDIR}/$NAME
  TMPD=/tmp/$NAME

  if [[ -f $NAME.vol.mp3 ]]; then
    echo "file $NAME.vol.mp3 is already there, skipping" >&2
    return
  fi

  $DEBUG mplayer -quiet -vo null -vc dummy -ao pcm:waveheader:file="$SHMD.wav" "$FILE"
  $DEBUG sox $SHMD.wav $TMPD.vol.wav vol $VOLUME speed $SPEED && $DEBUG rm $SHMD.wav
  $DEBUG ffmpeg -i $TMPD.vol.wav $NAME.vol.mp3 && $DEBUG rm $TMPD.vol.wav
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

for i; do
  make_loud $i
done
