#!/bin/bash
# simple lsof wrapper
# shows java processess only while adding the class name of the process via jps

if [[ "$1" =~ ^--?h(elp)?$ ]]; then
  lsof -h
  exit
fi

# at first load all java PIDs into asociative array to make this faster
declare -A JAVA_PIDS
while read PID CLASS; do
  JAVA_PIDS[$PID]=$CLASS
done < <(jps)

lsof $@ | grep ^java | {
while read IGNORE PID REST; do
  CLASS=${JAVA_PIDS[$PID]}
  # minor case: handle new process (created after init of JAVA_PIDS array)
  if [[ ! $CLASS ]]; then
    CLASS=$(jps | grep "^${PID}\ " | cut -d' ' -f2)
  fi
  echo $CLASS $PID $REST
done; } | column -t
