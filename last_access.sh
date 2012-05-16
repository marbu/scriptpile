#!/bin/bash
# show last access time along with filename for all files in given directory
# see: http://mywiki.wooledge.org/BashFAQ/020

find $1 -type f -print0 \
| while IFS= read -r -d $'\0' FILE; do
  READ=$(stat "$FILE" | sed -n '/^Access/s/.*\([0-9]\{4\}-..-..\).*/\1/p')
  echo "$READ:$FILE" 
done 
