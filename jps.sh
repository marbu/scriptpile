#!/bin/bash
# add effective username to the output of 'jps' command

if [[ "$1" =~ ^--?h(elp)?$ ]]; then
  jps -help
  exit
fi

jps $@ | {
while read PID CLASS; do
  USER=$(ps -p $PID -o ruser | tail -1)
  # when the process already doesn't exists, USER contains 'RUSER' string
  if [[ $USER != "RUSER" ]]; then
    echo -e "$PID\t$USER\t$CLASS"
  fi
done; }