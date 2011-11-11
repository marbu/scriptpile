#!/bin/bash
# simple script to backup home directory of given user
# by marbu, 2011

# configuration (TODO: move outside)
HOME_TO_BACKUP=/home/martin/tmp
REMOTE=scp://skoll/home/backup/dione/martin/
ENC_KEY=FB0CCD8C
SGN_KEY=16A500AE

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
        echo "- $DIRNAME$LINE"
      done < $i
    else
      echo "- ${DIRNAME}"
    fi
  done
}


#
# main
#

# create exclude filelist
# supposing /tmp is on encrypted volume
EXCLUDE_LIST_FILE=$(mktemp)
make_exclude_list $HOME_TO_BACKUP > $EXCLUDE_LIST_FILE

# run backup
duplicity \
  --encrypt-key $ENC_KEY --sign-key $SGN_KEY \
  --exclude-filelist $EXCLUDE_LIST_FILE \
  $HOME_TO_BACKUP $REMOTE

rm $EXCLUDE_LIST_FILE
