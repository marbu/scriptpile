#!/bin/bash
find $1 -print0 | xargs -0 -n 1 basename | sed 's/.*\././' | grep '^\.' | sort | uniq
