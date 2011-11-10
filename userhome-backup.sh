#!/bin/bash
# simple script to backup home directory of given user
# by marbu, 2011

# "do not backup" file indicates:
#  * this directory should be excluded from backup 
#  * or contains filenames of files excluded from backup
DNB_FN=".do_not_backup"

# create new exclude list based
# on DNB files
make_exclude_list() {
  LIST=$(find $1 -name $DNB_FN)
  for i in $LIST; do
    DIRNAME=${i%$DNB_FN}
    if [[ -s $i ]]; then
      while read LINE; do
        echo $DIRNAME$LINE
      done < $i
    else
      echo ${DIRNAME}
    fi
  done
}

make_exclude_list $1
