#!/bin/bash
# marbu's git helper, 2011
# create new git repo in certain directory and merge any git repo inside

# just using the subtree merge
# http://stackoverflow.com/questions/1425892/how-do-you-merge-two-git-repositories

show_help() {
  echo "Usage: $(basename $0) -p path_to_proposed_repo"
}

debug_msg() {
  if [[ $DEBUG ]]; then
    IFS=" "
    echo "DEBUG: $*" >&2
  fi
}

# initialize new git repo and commit untracked files from source dir
init_repo()
{
  git init
  mv ../"${TAMPER_DIR}"/* ../"${TAMPER_DIR}"/.[^.]* .
  git add .
  git commit -m "Initial import of untracked files"
}
  
# merge all found git repositories into new git repo
merge_repo()
{
  echo -e "\nMerging repository $REPO"
  REPO=$(echo $REPO | sed "s/$TAMPER_DIR/$TAMPER_REPO_DIR/")

  SUBDIR_NAME=$(echo "${REPO}" | sed "s!^${TAMPER_REPO_DIR}/!!" )
  BRANCH_NAME="$(basename ../${REPO})"
  debug_msg "REPO: $REPO, SUBDIR_NAME: $SUBDIR_NAME, BRANCH_NAME: $BRANCH_NAME"

  # merge the repo using subtree merge
  git remote add -f $BRANCH_NAME ../${REPO}
  git merge -s ours --no-commit $BRANCH_NAME
  git read-tree --prefix=${SUBDIR_NAME}/ -u ${BRANCH_NAME}/master
  git commit -m "Merge repository $BRANCH_NAME"
  git pull -s subtree $BRANCH_NAME master

  # remove remote branch and the branch itself
  git remote rm $BRANCH_NAME
  rm -rf ../${REPO}
}

mergedirs()
{
  # set names of directories (global variables)
  SOURCE_DIR="$1"
  TARGET_DIR="$1_repo"
  TAMPER_DIR="$1_tmp"
  TAMPER_REPO_DIR="$1_tmp_repo"

  # create tamper_dir
  cp -ar "$SOURCE_DIR" "$TAMPER_DIR"
  mkdir "$TAMPER_REPO_DIR"
  mkdir "$TARGET_DIR"

  # find git repos 
  REPO_LIST=$(find $TAMPER_DIR -name .git | sed 's!/.git$!!')

  # and move them to tamper_repo_dir
  IFS=$'\n'
  for REPO in $REPO_LIST; do
    echo "Found repo $REPO"

    # special case: repo not in root directory of source dir
    REPO_PATH=$(echo "$REPO" | sed "s@^$TAMPER_DIR/@@")
    #debug_msg "repo path init: $REPO_PATH"
    if echo $REPO_PATH | fgrep / > /dev/null ; then
      REPO_PATH=$(echo "$REPO_PATH" | sed 's!/[^/]*$!!')
      #debug_msg "repo path found: $REPO_PATH" # DEBUG
      mkdir -p "${TAMPER_REPO_DIR}/${REPO_PATH}"
      REPO_PATH="/${REPO_PATH}"
    else
      REPO_PATH=""
    fi

    #debug_msg repo path: ${REPO_PATH:-"none"}
    #debug_msg mv "${REPO}" "${REPO_PATH}${TAMPER_REPO_DIR}"
    mv "${REPO}" "${TAMPER_REPO_DIR}${REPO_PATH}"
  done

  echo
  cd "$TARGET_DIR"

  init_repo
  rmdir ../$TAMPER_DIR

  IFS=$'\n'
  for REPO in $REPO_LIST; do
    merge_repo
  done

  cd ..
  rm -rf $TAMPER_REPO_DIR
}

process_dir()
{
  if [[ ! -d $1 ]]; then
    echo "error: directory \'$1\' doesn't exist" >&2
    show_help
    return 1
  else
    mergedirs "$1"
  fi
}

#
# main
#

export LANG=C

if [[ $# = 0 ]]; then
  show_help
  exit
fi

if [[ $1 = "-d" ]]; then
  #set -o verbose
  DEBUG=echo
  shift
fi

case $1 in
  -p)      process_dir $2;;
  help)    show_help;;
  *)       show_help;;
esac
