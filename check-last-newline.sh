#!/bin/bash
# report error when given file doesn't end with newline on it's last line
# see also: https://stackoverflow.com/questions/729692/why-should-text-files-end-with-a-newline
last_char=$(tail -c 1 "$1" | od -v -An | sed 's/^\ *//')
if [[ ! $last_char ]]; then
  # file is empty, ok
  exit 0
fi
if [[ $last_char = "000012" ]]; then
  exit 0
else
  echo "$1" # >&2
  exit 1
fi
