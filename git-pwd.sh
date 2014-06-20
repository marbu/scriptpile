#!/bin/bash
# git-pwd: print working directory wrt to the location of git working tree

# try to get root directory of git repo, exit if no repo found
if ! GIT_ROOT=$(git rev-parse --show-toplevel); then
  exit 1
fi

if [[ "$PWD" = "$GIT_ROOT" ]]; then
  echo "/"
else
  echo ${PWD#"${GIT_ROOT}"}
fi
