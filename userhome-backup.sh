#!/bin/bash
# simple script to backup home directory of given user
# by marbu, 2011

# configuration (TODO: move outside)
HOME_TO_BACKUP=/mnt/snap_home/martin/
REMOTE=scp://skoll/dione/martin/
ENC_KEY=458EB91A
SGN_KEY=4A354563

help() {
  echo -e "duplicity home backup script\n"
  echo -e "Usage: $(basename $0) <command>\n"
  echo """Commands:
  show          show configuration
  du            show disk usage stats
  exlist        show list of excluded files
  run           run backup
  help          this text
"""
}

# "do not backup" file indicates:
#  * either entire directory should be excluded from backup 
#  * or contains filenames of files excluded from backup
DNB_FN=".do_not_backup"

# create new exclude list based on DNB files
# arg: dir to search in
make_exclude_list() {
  SOURCE_D=$1
  LIST=$(find $SOURCE_D -name $DNB_FN)
  for i in $LIST; do
    DIRNAME=${i%$DNB_FN}
    if [[ -s $i ]]; then
      while read LINE; do
        echo "$DIRNAME$LINE"
      done < $i
    else
      echo "${DIRNAME}"
    fi
  done
}

run_backup() {
  SOURCE_D=$1
  TARGET_D=$2

  # create list of excluded filenames
  # supposing /tmp is on encrypted volume
  EXCL_FLIST=$(mktemp)
  if [[ $DEBUG ]]; then
    make_exclude_list $SOURCE_D >&2
  else
    make_exclude_list $SOURCE_D | sed 's/^/- /' > $EXCL_FLIST
  fi

  $DEBUG /usr/bin/duplicity \
    --encrypt-key $ENC_KEY \
    --sign-key $SGN_KEY \
    --exclude-filelist $EXCL_FLIST \
    $SOURCE_D $TARGET_D

  rm $EXCL_FLIST
}

show_conf() {
  echo "local  dir: $HOME_TO_BACKUP"
  echo "remote dir: $REMOTE"
}

show_du() {
  SOURCE_D=$1
  # show how much space is being backed up
  EXCL_FLIST=$(mktemp)
  make_exclude_list $SOURCE_D > $EXCL_FLIST
  du -shc $(cat $EXCL_FLIST)
  # TODO: doesn't work
  # du -s --exclude-from=$EXCL_FLIST $SOURCE_D
  rm $EXCL_FLIST
}

#
# main
#

if [[ $# -eq 0 ]]; then
  help
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

case $1 in
  run)    run_backup $HOME_TO_BACKUP $REMOTE;;
  show)   show_conf;;
  du)     show_du $HOME_TO_BACKUP;;
  exlist) make_exclude_list $HOME_TO_BACKUP;;
  help)   help;;
  *)      help; exit 1;;
esac
