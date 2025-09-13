#!/bin/bash
# script to create new bare git remote in the shared dir

# debug/dry-run mode
if [[ $1 = "-d" ]]; then
  DRYRUNDEBUG=echo
  shift
fi

# find out root directory of current git repository
if ! GIT_ROOT=$(git rev-parse --show-toplevel); then
	exit 1;
fi
project=$(basename $GIT_ROOT)

# create new empty bare repo
$DRYRUNDEBUG git init --bare "/home/shared/git/${project}.git"
# create the new remote
$DRYRUNDEBUG git remote add shared "/home/shared/git/${project}.git"
