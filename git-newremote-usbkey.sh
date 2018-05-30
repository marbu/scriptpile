#!/bin/bash
# script to create new bare git remote on usb key and add this remote into the
# current project

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

# check if usbkey remote already exists
if git remote | grep usbkey > /dev/null; then
  echo "usbkey remote already exists:" >&2
  git remote -v | grep ^usbkey >&2
  exit 1;
fi

usbkey_mount=/media/sdb1

# check if usbkey is actually mounted
if ! mountpoint ${usbkey_mount} > /dev/null; then
  echo "usbkey is not mounted" >&2
  exit 1;
fi

# create new empty bare repo on the usbkey
$DRYRUNDEBUG git init --bare "${usbkey_mount}/git/${project}.git"
# create the new remote
$DRYRUNDEBUG git remote add usbkey "${usbkey_mount}/git/${project}.git"
