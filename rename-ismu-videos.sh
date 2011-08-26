#!/bin/bash
# fix names of lecture recordins from is mu

for i in *.avi; do
  if [[ ! $i =~ ^([A-Z]{2}[0-9]{3})-([12])-(D[123])-(20[0-9]{6}).avi ]]; then
    continue;
  fi
  CODE=${BASH_REMATCH[1]}
  PART=${BASH_REMATCH[2]}
  HALL=${BASH_REMATCH[3]}
  DATE=${BASH_REMATCH[4]}
  NEW_NAME=$CODE-$DATE-$HALL-$PART.avi
  mv $i $NEW_NAME
done
