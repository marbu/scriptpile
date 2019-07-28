#!/bin/bash
# Wrapper script for gtimelog (minimal time logging application) which makes
# sure the changes in it's data/log files are commited to a git repository in
# data directory.
# by marbu, Apache License 2.0, 2019

GTIMELOG_DIR=$(gtimelog --version | awk '/^Data/{print $3;}')

show_help()
{
  gtimelog $1
  echo "Additional Commands (inplemented in the wrapper):"
  echo "  sh, bash                   Run bash shell in data directory"
  echo "  cal                        Run git cal on data directory"
}

run_bash()
{
  cd "${GTIMELOG_DIR}"
  bash
}

run_git_cal()
{
  cd "${GTIMELOG_DIR}"
  git cal
}

is_git_initialized()
{
  git rev-parse --is-inside-work-tree > /dev/null
}

is_git_work_tree_clean()
{
  git diff-index --quiet HEAD --
}

gtimelog_wrapper()
{
  cd "${GTIMELOG_DIR}"
  if ! is_git_initialized; then
    git init .
  fi
  if ! is_git_work_tree_clean; then
    git add *
    git commit -m "pre gtimelog run cleanup commit"
  fi
  gtimelog "$*"
  git add *.txt && git commit -m "end of gtimelog session"
}

#
# main
#

if [[ $# = 0 ]]; then
  gtimelog_wrapper
  exit
fi

case $1 in
  sh|shell|bash)        run_bash;;
  cal)                  run_git_cal;;
  -h|--help|--help*)    show_help $1;;
  help)                 show_help -h;;
  *)                    gtimelog_wrapper "$*";;
esac
