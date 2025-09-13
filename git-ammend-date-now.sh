#!/bin/bash

show_help()
{
  echo "Usage: $(basename "$0") [TIMESTAMP]"
  echo "Where TIMESTAMP is something like 'Sep 13 13:13:33 2025 +0200'"
}

if [[ $1 = "-h" ]]; then
  show_help
  exit
fi

if [[ $# = 0 ]]; then
  export GIT_COMMITTER_DATE=$(date +'%b %e %T %Y %z')
else
  export GIT_COMMITTER_DATE=$1
fi

git commit --amend --no-edit --date "${GIT_COMMITTER_DATE}"
