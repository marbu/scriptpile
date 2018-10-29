#!/bin/bash
git log --oneline -- "$@" | cut -d' ' -f 1 | tac | nl | xargs -n 2 git format-patch -1 --start-number
