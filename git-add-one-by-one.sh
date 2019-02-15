#!/bin/bash

for i in *; do
  STATUS=$(git status -s "$i" | cut -d' ' -f 1)
  [[ ${STATUS} != "??" ]] && continue
  MDATE=$(stat "$i" | grep Modify: | cut -d' ' -f 2,3)
  git add "$i"
  git commit -m "add $i" --date="${MDATE}"
done
