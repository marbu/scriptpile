#!/bin/bash
LANG=C
IMAGE=winxp.image-001.7z
TARGET_DEV=/dev/sda1
/sbin/ntfsclone --save-image --output - $TARGET_DEV | /usr/bin/7za a -si $IMAGE
