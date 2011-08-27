#!/bin/bash

# TODO: add entries to ~/school/courses index file

help() {
	echo -n """make-sem.sh - create sem. directory structure
USAGE: make-sem.sh -s semester < courses
where courses consists of lines: name code [text only dir.]
"""
}

[[ $# -eq 0 ]] && { help; exit; }

#
# fce
#

SCHDIR="$HOME/school/"
PREFIX="${SCHDIR}sem."
# SEMDIR=${PREFIX}${SEM}
TEXTY="$HOME/texty/school.all/"

make_course() {
	CODE=$1
	NAME=$2
	TEXT_ONLY=$3

	mkdir ${TEXTY}/$CODE
	if [[ $TEXT_ONLY ]]; then
		cd $SEMDIR
		ln -s ${TEXTY}/$CODE $NAME
	else
		DIR="${SEMDIR}/$NAME"
		mkdir $DIR
		cd $DIR
		ln -s ${TEXTY}/$CODE texty
	fi
}

#
# getopts
#

while getopts s:h VOLBA; do
    case $VOLBA in
    s)    SEM=$OPTARG;;
    h)    help;
          exit 1;;
    esac
done

shift $(($OPTIND-1))

if ! [[ $SEM ]]; then
	echo "error: semester spec. missing" >&2
	help;
	exit 2
fi

#
# main
#

SEMDIR=${PREFIX}${SEM}

if [[ -d $SEMDIR  ]]; then
	echo "note: directory $SEMDIR already exists" >&2
else
	mkdir $SEMDIR || { echo "error: semdir can't be created" >&2; help; exit 3; }
fi

IFS=$'\n'
for i in $(grep -v ^#); do
	CODE=$(echo $i | cut -d' ' -f 1)
	NAME=$(echo $i | cut -d' ' -f 2)
	TEXT_ONLY=$(echo $i | cut -d' ' -f 3)
	make_course $CODE $NAME $TEXT_ONLY
done
