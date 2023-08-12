#!/bin/bash

set -ex

if dnf update -y; then
  if dnf needs-restarting --reboothint; then
    dnf needs-restarting --services | xargs systemctl restart
  else
    shutdown -r now
  fi
fi
