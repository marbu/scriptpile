#!/bin/bash

VIDEO_DIR=/home/shared/lectures
SEM_DIR=$HOME/school/sem/

show_help()
{
  echo -e "Usage: progname <command> [command-options]\n"
  echo """Commands:
  run   make missing links 
  help  this message"""
}

get_cr_dir()
{
  NAME=$(grep "$1" ~/school/courses | cut -d' ' -f2)
  [[ $NAME ]] && echo $SEM_DIR/$NAME
}

# make video link for each course with
# video files in current term
run()
{
  for CR in $VIDEO_DIR/*; do
    CR=${CR#"$VIDEO_DIR/"}
    [[ $DEBUG ]] && echo "trying $CR"
    CR_DIR=$(get_cr_dir $CR)
    if [[ $CR_DIR = "" ]]; then
      [[ $DEBUG ]] && echo "code $CR is not valid"
      continue
    fi
    if [[ ! -L "$CR_DIR/video" ]]; then
      cd "$CR_DIR"
      ln -s "$VIDEO_DIR/$CR" video
      cd - > /dev/null
	fi
  done
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

case $1 in
  -h|--help|help) show_help;;
  run)            run;;
esac
