#!/bin/bash

# A simple script to backup whole /home volume on rhea machine,
# see also:
# https://gist.github.com/marbu/ed5c2d2dc33e647b12307bb38306a9c8
# by marbu, 2017

set -e

WD_BACKUP_UUID=ee43a6cf-01a8-419a-8e2e-3b995e418995

#
# Check assumptions for the backup.
#

if [[ $(lsof /home 2>/dev/null | wc -l) -ne 0 ]]; then
  echo "There are open files in /home, see 'lsof /home' for details."
  echo "You need to make sure that no user (except root) is logged in."
  exit 1
fi

if [[ -b /dev/vg_rhea/lv_snap_home ]]; then
  echo "Snapshot of home volume is aready created, either it wasn't deleted"
  echo "during last backup, or the backup is still going on."
  exit 1
fi

if mountpoint /mnt/wd_backup_disk/; then
  echo "Directory /mnt/wd_backup_disk/ should not be mounted, try to run:"
  echo "umount /mnt/wd_backup_disk/ and retry."
  exit 1
fi

#
# Do the backup.
#

# mount target dist (where the backup will be stored)
mkdir -p /mnt/wd_backup_disk/
mount --uuid $WD_BACKUP_UUID -o rw /mnt/wd_backup_disk/

# create snapshot of /home
lvcreate --size 10G --name lv_snap_home --snapshot /dev/vg_rhea/lv_home
mkdir -p /mnt/snap_home/
mount -o ro /dev/vg_rhea/lv_snap_home /mnt/snap_home/

# run the backup
rsyncbtrfs backup /mnt/snap_home/ /mnt/wd_backup_disk/rhea_home_snapshots

# remove snapshot of /home
umount /mnt/snap_home/
lvremove -f /dev/vg_rhea/lv_snap_home
umount /mnt/wd_backup_disk/

# show user friendly final message
echo "Backup complete with success"
