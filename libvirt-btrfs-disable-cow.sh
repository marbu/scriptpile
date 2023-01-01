#!/bin/bash

# Disable fs COW for all qcow images in /var/lib/libvirt/images directory.

# expand non-matching globs to zero arguments, so that the for loop won't
# go through any iteration when no qcow images are found
shopt -s nullglob

IMAGES_DIR=/var/lib/libvirt/images

if [[ $1 = "-h" ]]; then
  echo "Disable filesystem COW on libvirt qcow images."
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  # shellcheck disable=SC2209
  DEBUG=echo
  shift
else
  unset DEBUG
fi

# Since Fedora 35, there is no libvird service, but virtqemud.service,
# virtlxcd.service and so on ...
# see https://fedoraproject.org/wiki/Changes/LibvirtModularDaemons
if [[ $DEBUG != echo ]] && systemctl is-active virtqemud.service > /dev/null; then
  echo "stop virtqemud service first (run 'systemctl stop virtqemud')"
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
