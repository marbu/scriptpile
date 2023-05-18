#!/bin/bash

# A simple script to backup whole /home volume on my dione machine, using
# btrfs snapshots and btrfs send/receive functionality. It replaces
# dione-btrfs-backup-saturn.sh script which I used before I moved /home volume
# to btrfs on dione, so it's quite opionated.
#
# By martinb@marbu.eu, Apache License 2.0, 2022

set -ex

# target btrfs device where the backup is saved
BACKUP_DEV=/dev/mapper/saturn_backup
BACKUP_MOUNT_DIR=/mnt/saturn_backup
# subvolume on the target backup device where the snapshots are stored
BACKUP_SNAPSHOT_DIR=${BACKUP_MOUNT_DIR}/dione_home_snapshots
# subvolume on the local machine with the snapshots
LOCAL_SNAPSHOT_DIR=/mnt/dione_home_snapshots

#
# Check assumptions for the backup.
#

if [[ $(lsof /home 2>/dev/null | wc -l) -ne 0 ]]; then
  echo "There are open files in /home, see 'lsof /home' for details."
  echo "You need to make sure that no user (except root) is logged in."
  exit 1
fi

if umount /home; then
  mount /home
else
  echo "Home volume can't be remounted (see the error above)."
  echo "You need to make sure that remounting is possible to continue."
  exit 1
fi

if mountpoint ${BACKUP_MOUNT_DIR}/ >/dev/null; then
  echo "Directory ${BACKUP_MOUNT_DIR}/ should not be mounted, try to run:"
  echo "umount ${BACKUP_MOUNT_DIR}/ and retry."
  exit 1
fi

if ! mountpoint ${LOCAL_SNAPSHOT_DIR}/ >/dev/null; then
  mount ${LOCAL_SNAPSHOT_DIR}
fi

#
# Do the backup.
#

# mount target dir (where the backup will be stored)
mkdir -p ${BACKUP_MOUNT_DIR}/
mount ${BACKUP_DEV} -o rw ${BACKUP_MOUNT_DIR}/

# create new local ro snapshot of /home in /mnt/dione_home_snapshots
SNAP_TS=$(date '+%F-%T')
SNAP_HOME=${LOCAL_SNAPSHOT_DIR}/${SNAP_TS}
btrfs subvolume snapshot -r /home "${SNAP_HOME}"
sync

# compute sha1 checksum of /home
TMPSHA=$(mktemp)
SHA_NAME=checksum.${SNAP_TS}.sha1
cd "$SNAP_HOME"
find . -type f -print0 | xargs -0 sha1sum > "$TMPSHA"
cd -

# copy the sha1 sum file back to original home volume and the local snapshot
cp --archive "$TMPSHA" "/home/$SHA_NAME"
btrfs property set -t subvol "${SNAP_HOME}" ro false
cp --archive "$TMPSHA" "${SNAP_HOME}/$SHA_NAME"
btrfs property set -t subvol "${SNAP_HOME}" ro true
rm "$TMPSHA"

# find the latest previous snapshot
for SNAP in $(ls -r ${LOCAL_SNAPSHOT_DIR}); do
  if [[ -d "${BACKUP_SNAPSHOT_DIR}/${SNAP}" ]]; then
    # PREV_SNAP="/mnt/dione_home_snapshots/2022-08-13-23:05:42"
    PREV_SNAP="${LOCAL_SNAPSHOT_DIR}/${SNAP}"
    break
  fi
done

if [[ -z "${PREV_SNAP}" ]]; then
  echo "No local snapshot has been previously backed up on the backup device."
  exit 1
fi

# run the backup via send/receive
btrfs send -p "${PREV_SNAP}" "${SNAP_HOME}" | btrfs receive ${BACKUP_SNAPSHOT_DIR}

# if all went well, let's update the current symlink on the target device
cd ${BACKUP_SNAPSHOT_DIR}
PREV_CUR=$(readlink cur)
rm cur
ln -s "${SNAP_TS}" cur
cd -
echo "Updated 'cur' symlink from $PREV_CUR to $SNAP_TS"

# if we can find id of the target snapshot dir, let's update it's cur-id link
# in the local snapshot dir
BSD_ID_FILE=${BACKUP_SNAPSHOT_DIR}/.id
if [[ -e ${BSD_ID_FILE} ]]; then
  BSD_ID=$(cat ${BSD_ID_FILE})
  cd ${LOCAL_SNAPSHOT_DIR}
  rm -f cur-${BSD_ID}
  ln -s "${SNAP_TS}" cur-${BSD_ID}
  cd -
fi

# umount the tartet dir (making sure data are there) and the local snapshot
# volume (we no longer need it available)
sync
umount ${BACKUP_MOUNT_DIR}
umount ${LOCAL_SNAPSHOT_DIR}

# show user friendly final message
echo "Backup completed with success"

echo "And now ... scrub"
mount ${BACKUP_DEV} -o rw ${BACKUP_MOUNT_DIR}/
btrfs scrub status ${BACKUP_MOUNT_DIR}/
btrfs scrub start  ${BACKUP_MOUNT_DIR}/
