#!/bin/bash
# just show remote url for all git repos in $(pwd)
for i in */.git; do
  cd ${i%/.git}
  git remote -v \
  | head -1 \
  | sed 's/^origin\t\(.*\)\ (fetch)$/\1/'
  cd - >/dev/null
done
