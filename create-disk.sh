#!/bin/bash
mkdir /mnt/ramdisk
mount -t tmpfs none /mnt/ramdisk -o size=300m
dd if=/dev/zero of=/mnt/ramdisk/bigsecret bs=1048576 count=300
losetup /dev/loop0 /mnt/ramdisk/bigsecret
