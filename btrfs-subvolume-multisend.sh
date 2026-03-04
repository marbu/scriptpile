#!/bin/bash

# A simple script to transfer btrfs snapshots from one subvolume to another,
# by martinb@marbu.eu, Apache License 2.0, 2026

SCRIPTNAME=$(basename "$0")
SNAPSHOTS=()

show_help()
{
  echo "For given btrfs subvolume mounted at ORIGIN_PATH with many snapshot"
  echo "subvolumes inside, copy subvolumes starting FIRST_VOL_NAME until the"
  echo "lastest one to another btrfs filesystem subvolume at TARGET_PATH using"
  echo "btrfs send/receive feature."
  echo
  echo "Usage: ${SCRIPTNAME} [-d] ORIGIN_PATH FIRST_VOL_NAME TARGET_PATH"
  echo
  echo "  -d   dry/debug mode (don't perform any actions, just print commands)"
  echo "  -x   use 'set -x' to indicate what is happening"
  echo "  -h   show help (this message)"
}

get_snapshots()
{
  ORIGIN_D=$1
  SN_FIRST=$2
  FOUND=0
  ORIGIN_NAME=$(basename "$ORIGIN_D")
  while IFS= read -r LINE; do
    if [[ ${FOUND} -eq 0 ]]; then
      if [[ "${LINE}" =~ ${ORIGIN_NAME}\/${SN_FIRST}$ ]]; then
        SNAPSHOTS+=("${SN_FIRST}")
        FOUND=1
      else
        continue
      fi
    else
      SNAP_PATH=$(cut -d$'\t' -f 7 <<< "${LINE}")
      SNAP_NAME=$(basename "${SNAP_PATH}")
      SNAPSHOTS+=("${SNAP_NAME}")
    fi
  done < <(btrfs subvolume list -o "${ORIGIN_D}" -s -t | tail -n +3)
}

#
# main
#

if [[ $# = 0 ]]; then
  show_help
  exit
fi

unset DEBUG
unset VERBOSE

while getopts "dxh" OPT; do
  case $OPT in
  d)  DEBUG=echo;;
  x)  TRACE=1;;
  h)  show_help;
      exit;;
  *)  echo;
      show_help;
      exit 1;;
  esac
done

shift $((OPTIND-1))

ORIGIN_D=$1
SN_FIRST=$2
TARGET_D=$3

get_snapshots "${ORIGIN_D}" "${SN_FIRST}"

SNAP_LEN=${#SNAPSHOTS[@]}

if [[ ! -d "${ORIGIN_D}/${SN_FIRST}" ]]; then
  echo "error: first source snapshot doesn't exist" >&2
  exit 1
fi

if [[ ${TRACE} ]]; then
  set -x
fi

# send the first snapshots if it's not already present in the target volume
if [[ ! -d "${TARGET_D}/${SN_FIRST}" ]]; then
  if [[ ${DEBUG} ]]; then
    echo btrfs send "${ORIGIN_D}/${SN_FIRST}" \| btrfs receive "${TARGET_D}"
  else
    btrfs send "${ORIGIN_D}/${SN_FIRST}" | btrfs receive "${TARGET_D}"
    if [[ $? -ne 0 ]]; then
      echo "error: transfer of the first snapshot failed" >&2
      exit 1
    fi
  fi
fi

# send the remaining snapshots as incremental stream, referencing parent
for i in $(seq 1 $((SNAP_LEN - 1))); do
  if [[ ${DEBUG} ]]; then
    echo btrfs send -p "${ORIGIN_D}/${SNAPSHOTS[(($i-1))]}" "${ORIGIN_D}/${SNAPSHOTS[$i]}" \| btrfs receive "${TARGET_D}"
  else
    btrfs send -p "${ORIGIN_D}/${SNAPSHOTS[(($i-1))]}" "${ORIGIN_D}/${SNAPSHOTS[$i]}" | btrfs receive "${TARGET_D}"
  fi
done
