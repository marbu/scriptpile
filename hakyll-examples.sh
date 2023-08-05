#!/bin/bash
# Fetch all main pages of web sites from hakyll examples list.

for URL in $(sed -n 's/^- <\(.*\)>,/\1/p' ~/projects/hakyll/web/examples.markdown); do
  FILE=$(basename $URL).html
  LOGS=$(basename $URL).log
  echo -n "Fetching $URL"
  wget --timeout 30 -o "$LOGS" -O "$FILE" "$URL"
  # keep logs only when the download fails
  if [[ $? -eq 0 ]]; then
    rm "$LOGS"
  fi
  echo " done"
done
