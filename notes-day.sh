#!/bin/bash

show_help()
{
  echo "Usage: $(basename $0) NOTE_DIR NOTE_FILES"
  echo
  echo "Options:"
  echo "  NOTE_DIR   - directory with notes repository"
  echo "  NOTE_FILES - files to edit and commit"
}

die() {
  echo "error: $1" 1>&2
  exit 1
}

run_edit()
{
  NOTE_DIR=$1
  shift
  NOTE_FILES=$@

  cd $NOTE_DIR || die "$NOTE_DIR can't be used as a NOTE_DIR"

  NOW=$(date '+%Y-%m-%d')
  LAST=$(git log --pretty=oneline | head -1 | cut -d' ' -f 2)
  $DEBUG && echo "# now: $NOW, last: $LAST"

  $DEBUG vim -O $NOTE_FILES
  $DEBUG git add $NOTE_FILES

  if [[ $NOW = $LAST ]]; then
    # we haven't finished yet
    $DEBUG git commit --amend -m $NOW
  else
    $DEBUG git commit -m $NOW
  fi
}

#
# main
#

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

if [[ $# -lt 2 ]]; then
  show_help
  exit
fi

run_edit $@
