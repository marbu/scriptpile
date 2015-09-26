#!/bin/bash

# Poor man's luks encryption password recovery.
# It's usefull only if:
#  - you have forgotten luks password
#  - but you still have some basic idea how it looked like
#    (you are able to write down file with possible passwords)
#  - number of possible passwords is small

luks_dev=/dev/mapper/loop0p6
dictfile=password.list

cat $dictfile | while read pass; do
  echo $pass | cryptsetup luksOpen $luks_dev --test-passphrase -T1
  if [[ $? -eq 0 ]]; then
    echo "found password: \"$pass\""
    exit 0
  fi
done
exit 1
