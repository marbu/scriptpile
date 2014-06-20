#!/bin/bash
# git-realpath.sh

show_help()
{
  echo "Usage: $(basename $0) [option] file"
  echo "Print the resolved absolute file name wrt root of git working tree;"
  echo "all but the last component must exist"
}

#
# main
#

if [[ $# = 0 ]]; then
  show_help
  exit
fi

if [[ "$1" =~ ^--?h(elp)?$ ]]; then
  show_help
  realpath --help | tail -n+4
  exit
fi

# try to get root directory of git repo, exit if no repo found
if ! GIT_ROOT=$(git rev-parse --show-toplevel); then
  exit 1
fi

#realpath --relative-to="$GIT_ROOT" $@ | sed 's!^!/!'
realpath $@ | sed "s#^$GIT_ROOT##"
