#!/bin/bash

FPID=$(ps aux \
 | grep libflashplayer \
 | grep -v 'grep.*libflashplayer' \
 | awk '{ print $2 }' \
 )

if [[ $# = 0 ]]; then
  echo $FPID
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

for pid in $FPID; do
  echo PID: $pid >&2
  case $1 in
    fd)  $DEBUG ls --color -l /proc/$pid/fd;;
    ip)  lsof -p $pid | grep IPv[46];;
	*)   :;;
  esac
done
