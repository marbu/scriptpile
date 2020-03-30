#!/bin/bash

# Disable fs COW for all qcow images in /var/lib/libvirt/images directory.

IMAGES_DIR=/var/lib/libvirt/images

if [[ $1 = "-h" ]]; then
  echo "Disable filesystem COW on libvirt qcow images."
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

if systemctl is-active libvirtd.service > /dev/null; then
  echo "stop libvirt service first (run 'systemctl stop libvirtd')"
  exit 1
fi

# create tmp dir
TMP_DIR="${IMAGES_DIR}"/tmp
$DEBUG mkdir -p "${TMP_DIR}"

# disable COW, effective for new files in the dir only
$DEBUG chattr +C "${IMAGES_DIR}"

for IMG in "${IMAGES_DIR}"/*.qcow*; do
  if lsof "${IMG}" > /dev/null; then
    echo "image $IMG is being used, skipping"
	continue
  fi
  if lsattr "${IMG}" | cut -d' ' -f1 | grep C > /dev/null; then
    echo "image $IMG already has C attribute, skipping"
	continue
  fi
  TMP_FILE="${TMP_DIR}"/$(basename "$IMG")
  $DEBUG mv "${IMG}" "${TMP_FILE}"
  $DEBUG cp -a "${TMP_FILE}" "${IMAGES_DIR}"
  $DEBUG rm "${TMP_FILE}"
done

$DEBUG rmdir "${IMAGES_DIR}"/tmp
