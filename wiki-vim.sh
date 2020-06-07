#!/bin/bash

WIKIDIR=~/tvorba/wiki
WIKIURL=http://localhost:50505/

if [[ $# = 0 || $1 = "-h"  ]]; then
  echo "Open gitit wikipage in vim via it's url"
  echo "Usage: $(basename $0) WIKIPAGE_URL"
  exit
fi

if [[ "$1" == "$WIKIURL"* ]]; then
  vim "${WIKIDIR}/${1#$WIKIURL}.page"
else
  echo "error: \"$1\" is not a valid wikipage url"
  exit 1
fi
