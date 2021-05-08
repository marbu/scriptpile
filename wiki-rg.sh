#!/bin/bash

WIKIDIR=~/tvorba/wiki

if [[ $(pwd) == $(realpath "$WIKIDIR")* ]]; then
  # we are in the wiki dir, let's search in current directory only
  WIKIDIR="."
fi

for i in $@; do
  rg "$i" $WIKIDIR
  echo
done
