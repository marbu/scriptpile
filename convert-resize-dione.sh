#!/bin/bash
NEW_GEOMETRY=1920x1080
for i in $*; do
  convert -resize $NEW_GEOMETRY "$i" "${i%jpg}${NEW_GEOMETRY}.jpg"
done
