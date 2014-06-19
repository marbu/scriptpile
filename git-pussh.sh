#!/bin/bash

# Push updates to remote branch which is checked out in working tree.
# This script expects that:
#  - remote branch is clean
#  - remote is accessed via ssh with passwordless cert/enabled ssh agent 

show_help()
{
  echo "Usage: $(basename $0) <remote> <branch> [-f]"
}

ssh_push()
{
  local REMOTE=$1
  local BRANCH=$2
  local FORCE=$3

  # repo description, eg.: 'test.marbu.eu:~/tmp/foo/.git'
  REPO=$(git remote -v | grep '(push)' | grep "$REMOTE" | awk '{ print $2 }')

  # hostname of the remote, eg. 'test.marbu.eu'
  if [[ "$REPO" =~ ^ssh://([^/]+)(/.*) ]]; then
    HOST_NAME=${BASH_REMATCH[1]}
	GIT_REPO=${BASH_REMATCH[2]}
  else
    HOST_NAME=$(cut -d':' -f 1 <<< ${REPO})
    GIT_REPO=$(cut -d':' -f 2 <<< ${REPO} | sed 's/~/\$HOME/')
  fi

  GIT_TREE=$(sed 's/~/\$HOME/' <<< ${GIT_REPO%.git})

  GIT_CMD="git --git-dir=$GIT_REPO --work-tree=$GIT_TREE"
  SHOW_BRANCH="rev-parse --abbrev-ref HEAD"

  # we need to know current branch to be able to switch back later
  # because 'git checkout -' may not always work
  if [[ $DEBUG ]]; then
    echo "PREV_BRANCH=\$(ssh $HOST_NAME \"$GIT_CMD $SHOW_BRANCH\")"
  else
    PREV_BRANCH=$(ssh "$HOST_NAME" "$GIT_CMD $SHOW_BRANCH")
  fi

  $DEBUG ssh "$HOST_NAME" "$GIT_CMD checkout -b __pussh_tmp"
  $DEBUG git push "$FORCE" "$REMOTE" "$BRANCH"
  $DEBUG ssh "$HOST_NAME" "$GIT_CMD checkout ${PREV_BRANCH:-\$PREV_BRANCH}"
  $DEBUG ssh "$HOST_NAME" "$GIT_CMD branch -D __pussh_tmp"
}

#
# main
#

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

if [[ $# != 2 && $# != 3 ]]; then
  show_help
  exit
fi

case $1 in
  help|-h|--help) show_help;;
  *)              ssh_push "$1" "$2" "$3";;
esac
