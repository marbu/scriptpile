#!/bin/bash
# simple lsof wrapper
# shows java processess only while adding the class name of the process via jps

if [[ "$1" =~ ^--?h(elp)?$ ]]; then
  lsof -h
  exit
fi

lsof $@ | grep ^java | {
while read IGNORE PID REST; do
  CLASS=$(jps | grep "^${PID}\ " | cut -d' ' -f2)
  echo $CLASS $PID $REST
done; }
