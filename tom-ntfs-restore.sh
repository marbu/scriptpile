#!/bin/bash
LANG=C
IMAGE=winxp.image-001.7z
TARGET_DEV=/dev/sda1
/usr/bin/7za e -so $IMAGE | /sbin/ntfsclone --restore-image --overwrite $TARGET_DEV -
