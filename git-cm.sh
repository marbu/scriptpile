#!/bin/bash

show_help()
{
  echo "$(basename "$0"): git helper to avoid quoting long commit messages by hand"
  echo
  echo "Usage: $(basename "$0") <commit message with spaces>"
}

#
# main
#

if [[ $# = 0 || $1 = "-h" ]]; then
  show_help
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  # shellcheck disable=SC2209
  DEBUG=echo
  shift
else
  unset DEBUG
fi

$DEBUG git commit -m "$*"
