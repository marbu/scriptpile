#!/bin/bash

URL="http://www.howmanypeopleareinspacerightnow.com/"
FILE="$HOME/local/var/spacepeoplehistory"

help() {
	echo $0 - wget based sript;
}

[[ $1 = "-h" ]] && { help; exit; }
[[ -e $FILE ]] || touch $FILE

DAY=$(date '+%Y-%m-%d')

if grep $DAY $FILE &> /dev/null; then
	grep $DAY $FILE | cut -d' ' -f2
else
	NUM=$(wget ${URL} -O - 2> /dev/null | grep "<h2>" | sed 's!^.*<h2>\([0-9]\+\)</h2>.*!\1!')
	echo $NUM
	echo $DAY $NUM >> $FILE
fi
