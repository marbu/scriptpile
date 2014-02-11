#!/bin/bash
# add effective username to the output of 'jps' command

if [[ "$1" =~ ^--?h(elp)?$ ]]; then
  jps -help
  exit
fi

PID_FILE=$(mktemp /tmp/jps.XXXXXXXX.pid)

{ jps $@ & echo $! > $PID_FILE; } | {
JPS_PID=$(cat $PID_FILE)
rm $PID_FILE
while read PID CLASS; do
  # don't show jps process itself
  if [[ $JPS_PID = $PID ]]; then
    continue
  fi
  USER=$(ps -p $PID -o ruser | tail -1)
  # when the process already doesn't exists, USER contains 'RUSER' string
  if [[ $USER != "RUSER" ]]; then
    echo -e "$PID\t$USER\t$CLASS"
  fi
done; } | column -t
