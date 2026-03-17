#!/bin/bash

# A simple script to run backup if the backup device (aka TBL) is present.
#
# By martinb@marbu.eu, Apache License 2.0, 2026

# The target backup device
TBL_UUID=26479192-4c60-4214-a42c-d1ec74a326f5
TBL_DEV=/dev/disk/by-uuid/${TBL_UUID}
TBL_LUKS_NAME=luks-tbl
TBL_KEY_FILE=/etc/cryptsetup-keys.d/tbl.key

set -ex

if ! mountpoint /home; then
  mount /home
fi

if [[ -h "${TBL_DEV}" ]]; then
  cryptsetup luksOpen "${TBL_DEV}" "${TBL_LUKS_NAME}" --key-file "${TBL_KEY_FILE}"
  dione-btrfs-send-backup-saturn.sh -q -b "/dev/mapper/${TBL_LUKS_NAME}"
  cryptsetup luksClose "${TBL_LUKS_NAME}"
else
  echo "target backup device not found"
  dione-btrfs-send-backup-saturn.sh -qs
fi

umount /home
