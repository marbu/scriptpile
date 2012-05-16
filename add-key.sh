#!/usr/bin/env bash
# publickey add helper (for midpssh)

if [[ $# = 0 ]]; then
  echo "add-key key"
  exit
fi

echo "$*" >> /home/marbu/.ssh/authorized_keys
