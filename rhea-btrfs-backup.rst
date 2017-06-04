=============
 Rhea Backup
=============

:target device: external 1TB HDD via usb 3
:filesystem: btrfs

Strategy:

* Whole ``/home`` for full user data backup.
* Use *lvm2 snapshots* to freeze state of ``/home`` during backup.
  Also consider btrfs in the future.
* Running under root, automated via script.
* Use mirror like approach for easy access, while keeping multiple snapshots
  of older backup batches.
* Easy read-only access to the old snapshots.

Backup software
===============

Either one of:

* file backup/mirroring to btrfs on external drive
* file backup/mirroring to ext4 on external drive
* rsync pushes to btrfs subvolume

Software to consider:

* sync/mirroring: `rsync-backup <http://www.nongnu.org/rdiff-backup/>`_
* file-based: `rsnapshot <http://rsnapshot.org/faq.html>`_

Or just btrfs snapshots with some script over it.

Btrfs
=====

See:

* https://wiki.archlinux.org/index.php/Btrfs
* https://btrfs.wiki.kernel.org/index.php/Main_Page
  good for reference:
  * https://btrfs.wiki.kernel.org/index.php/Manpage/mkfs.btrfs
  * https://btrfs.wiki.kernel.org/index.php/SysadminGuide
  * https://btrfs.wiki.kernel.org/index.php/UseCases
  * https://btrfs.wiki.kernel.org/index.php/Incremental_Backup

To get disk usage::

    # btrfs filesystem df /
    # btrfs filesystem show /dev/sda
    # btrfs filesystem usage /

Subvolumes and snapshots::

    # btrfs subvolume create /path/to/subvolume
    # btrfs subvolume list path
    # btrfs subvolume snapshot source [dest/]name

Compression::

    # btrfs filesystem defragment -r -v -clzo /
    # mount -o compress=lzo /dev/sdxY /mnt/

Send and Receive::

    # btrfs send /root_backup | btrfs receive /backup

Details
~~~~~~~

Multiple fs trees, fs tree corresponds to a subvolume. The main tree has id 5,
while first-created subvolume 256.

Withins fs tree, objects has independent inode number.

Mounting a subvolume also makes any of its nested child subvolumes available at
their respective location relative to the mount-point.

A Btrfs filesystem has a *default subvolume*, which is initially set to be the
top-level subvolume and which is mounted if no subvol or subvolid option is
specified.

Tip: Changing subvolume layouts is made simpler by not using the toplevel
subvolume (ID=5) as / (which is done by default). Instead, consider creating a
subvolume to house your actual data and mounting it as /. See *Flat Layout*.

Changing the default subvolume with btrfs subvolume default will make the top
level of the filesystem inaccessible, except by use of the subvol=/ or
subvolid=5 mount options. Note: this is not what Fedora does or is suggested
for Flat Layout scheme.

A *snapshot* is simply a subvolume that shares its data (and metadata) with
some other subvolume, using Btrfs's COW capabilities.

Incremental Backup backed by btrfs use cases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Based on *How can I use btrfs for backups/time-machine?* and
https://btrfs.wiki.kernel.org/index.php/Incremental_Backup on btrfs wiki:

* https://github.com/jonhiggs/btrfs-time-machine
* https://github.com/oxplot/rsyncbtrfs TODO
* https://github.com/digint/btrbk TODO
  https://digint.ch/btrbk/
  (see backup from non-btrfs source)

In general:

* https://btrfs.wiki.kernel.org/index.php/Incremental_Backup
* https://serverfault.com/questions/356397/btrfs-enabled-backup-solution
* http://www.sanitarium.net/golug/rsync+btrfs_backups_2011.html
* https://a3nm.net/blog/btrfs_giving_up.html
* https://www.mendix.com/blog/btrfs-dirvish-perfect-match/

See also complex tools (or not exactly fitting my use case):

* https://github.com/ruediste/btrbck (java)
* urbackup.org (client server setup) which uses this approach:
  http://blog.urbackup.org/83/file-backup-storage-with-btrfs-snapshots
* https://github.com/AmesCornish/buttersink

Good example (on Arch Linux) when one uses btrfs on the workstation as well:
https://ramsdenj.com/2016/04/05/using-btrfs-for-easy-backup-and-rollback.html
(tools used: btrfs, snapper, btrbk, ..)

Actual setup
~~~~~~~~~~~~

Create filesystem directly on the device::

    # mkfs.btrfs -L wd_backup_disk /dev/sdb
    btrfs-progs v4.6.1
    See http://btrfs.wiki.kernel.org for more information.

    Label:              wd_backup_disk
    UUID:               ee43a6cf-01a8-419a-8e2e-3b995e418995
    Node size:          16384
    Sector size:        4096
    Filesystem size:    931.48GiB
    Block group profiles:
      Data:             single            8.00MiB
      Metadata:         DUP               1.01GiB
      System:           DUP              12.00MiB
    SSD detected:       no
    Incompat features:  extref, skinny-metadata
    Number of devices:  1
    Devices:
       ID        SIZE  PATH
        1   931.48GiB  /dev/sdb

    # mount /dev/sdb /mnt/wd_backup_disk/

Testing rsyncbtrfs::

    # btrfs subvolume create /mnt/wd_backup_disk/phoebe_snapshots
    # mkdir /mnt/wd_backup_disk/phoebe_snapshots/martin
    # rsyncbtrfs init /mnt/wd_backup_disk/phoebe_snapshots/martin/
    # rsyncbtrfs backup /home/martin /mnt/wd_backup_disk/phoebe_snapshots/martin/
    Create subvolume '/mnt/wd_backup_disk/phoebe_snapshots/martin//.inprog-CRIELdI/vol'
    # ls -l /mnt/wd_backup_disk/phoebe_snapshots/martin/
    total 4
    drwx------. 1 martin martin 592 May  5 19:49 2017-05-08-13:22:39
    lrwxrwxrwx. 1 root  root   19 May  8 13:34 cur -> 2017-05-08-13:22:39

Backing up home on rhea::

    # lvcreate --size 10G --name lv_snap_home --snapshot /dev/vg_rhea/lv_home
    # mkdir /mnt/snap_home
    # mount -o ro /dev/vg_rhea/lv_snap_home /mnt/snap_home/
    # mount /dev/sdg /mnt/wd_backup_disk/
    # btrfs subvolume create /mnt/wd_backup_disk/rhea_home_snapshots
    # rsyncbtrfs init /mnt/wd_backup_disk/rhea_home_snapshots
    # rsyncbtrfs backup /mnt/snap_home/ /mnt/wd_backup_disk/rhea_home_snapshots
    # umount /mnt/snap_home/
    # lvremove /dev/vg_rhea/lv_snap_home
    # ls -l /mnt/wd_backup_disk/rhea_home_snapshots/
    total 4
    drwxr-xr-x. 1 root root 106 Feb  3  2016 2017-05-08-14:29:00
    lrwxrwxrwx. 1 root root  19 May  8 18:23 cur -> 2017-05-08-14:29:00
    # umount /mnt/wd_backup_disk/

Read only setup for reading snaphosts, new fstab line::

   UUID=ee43a6cf-01a8-419a-8e2e-3b995e418995 /mnt/wd_backup_disk btrfs defaults,noauto,subvol=rhea_home_snapshots,ro 0 0
