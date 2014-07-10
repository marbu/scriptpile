#!/bin/bash
# create a patch following bigtop workflow
# https://cwiki.apache.org/confluence/display/BIGTOP/How+to+Contribute

# directory where to save the patch
PATCH_DIR=~/tvorba/patch

show_help()
{
  echo "$(basename $0): create a bigtop patch"
}

die()
{
  echo "error: $1" 1>&2
  exit 1
}

get_patch_name()
{
  local BIGTOP_JIRA=$1
  NAME_BASE=${PATCH_DIR}/${BIGTOP_JIRA}
  N=1
  while [[ -e "${NAME_BASE}.${N}.patch" ]]; do
    : $((N++))
  done
  echo "${NAME_BASE}.${N}.patch"
}

make_patch()
{
  GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  if [[ ${GIT_BRANCH}  =~ ^local_(BIGTOP-[0-9]+).*$ ]]; then
    BIGTOP_JIRA=${BASH_REMATCH[1]}
  else
    die "name of current branch doesn't follow regexp local_BIGTOP-[0-9]+"
  fi
  PATCH_NAME=$(get_patch_name ${BIGTOP_JIRA})
  GIT_FORMAT_PATCH="git format-patch HEAD^..HEAD --stdout"
  if [[ $DEBUG ]]; then
    echo $GIT_FORMAT_PATCH \> ${PATCH_NAME}
  else
    $GIT_FORMAT_PATCH > ${PATCH_NAME}
  fi
}

#
# main
#

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

case $1 in
  -h|--help|help) show_help;;
  *)              make_patch;;
esac
