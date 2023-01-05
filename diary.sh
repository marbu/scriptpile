#!/bin/bash

D_DIR=~/tvorba/diary/

show_help()
{
  echo "Open a diary file (for today or given day) in vim."
  echo
  echo "Usage: $(basename "$0") [GNU date human readable syntax]"
  echo
  echo "Examples:"
  echo
  echo "$(basename "$0")              open diary for today"
  echo "$(basename "$0") yesterday    open diary for yesterday"
  echo "$(basename "$0") last Friday  open diar for last Friday"
}

if [[ $# = 1 && "$1" =~ ^-?-?h(elp)?$ ]]; then
  show_help
  exit
fi

if [[ $# = 0 ]]; then
  D_FILE=$(date '+%F')
else
  D_FILE=$(date '+%F' --date="$*")
fi

if [[ -z $D_FILE ]]; then
  exit 1
fi

DPATH=${D_DIR}/${D_FILE}.md
if [[ ! -s "${DPATH}" ]]; then
  echo -e "## ${D_FILE}\n\n" > "${DPATH}"
fi
vim "${DPATH}"
