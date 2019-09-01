#!/bin/bash

# A simple script to backup whole /home volume on dione machine,
# see also:
# https://gist.github.com/marbu/ed5c2d2dc33e647b12307bb38306a9c8
# by marbu, 2017, 2018

set -e

# target btrfs device where backup is saved
BACKUP_DEV=/dev/mapper/saturn_backup
BACKUP_MOUNT_DIR=saturn_backup
BACKUP_SUBVOLUME=dione_home_snapshots

# home volume we are going to backup
ORIGIN_VG=fedora_dione
ORIGIN_LV=home

#
# Check assumptions for the backup.
#

if [[ $(lsof /home 2>/dev/null | wc -l) -ne 0 ]]; then
  echo "There are open files in /home, see 'lsof /home' for details."
  echo "You need to make sure that no user (except root) is logged in."
  exit 1
fi

if [[ -b /dev/${ORIGIN_VG}/snap_home ]]; then
  echo "Snapshot of home volume is aready created, either it wasn't deleted"
  echo "during last backup, or the backup is still going on."
  exit 1
fi

if mountpoint /mnt/${BACKUP_MOUNT_DIR}/ >/dev/null; then
  echo "Directory /mnt/${BACKUP_MOUNT_DIR}/ should not be mounted, try to run:"
  echo "umount /mnt/${BACKUP_MOUNT_DIR}/ and retry."
  exit 1
fi

#
# Do the backup.
#

# mount target dir (where the backup will be stored)
mkdir -p /mnt/${BACKUP_MOUNT_DIR}/
mount ${BACKUP_DEV} -o rw /mnt/${BACKUP_MOUNT_DIR}/

# create snapshot of /home
umount /home
lvcreate --name snap_home --snapshot /dev/${ORIGIN_VG}/${ORIGIN_LV}
lvchange -ay -K ${ORIGIN_VG}/snap_home
mkdir -p /mnt/snap_home/
mount -o ro /dev/${ORIGIN_VG}/snap_home /mnt/snap_home/
mount /home

# compute sha1 checksum of /home
TMPSHA=$(mktemp)
SHA_NAME=checksum.$(date -Idate).sha1
cd /home
find . -type f -print0 | xargs -0 sha1sum > "$TMPSHA"
cd -

# run the backup
rsyncbtrfs backup /mnt/snap_home/ /mnt/${BACKUP_MOUNT_DIR}/${BACKUP_SUBVOLUME}

# copy the sha1 sum file back to original home volume and the backup dir
cp "$TMPSHA" /home/$SHA_NAME
cp "$TMPSHA" /mnt/${BACKUP_MOUNT_DIR}/${BACKUP_SUBVOLUME}/$SHA_NAME/cur
rm "$TMPSHA"

# remove snapshot of /home
umount /mnt/snap_home/
lvchange -an ${ORIGIN_VG}/snap_home
lvremove -f /dev/${ORIGIN_VG}/snap_home

# umount tartet dir
umount /mnt/${BACKUP_MOUNT_DIR}/

# show user friendly final message
echo "Backup completed with success"
