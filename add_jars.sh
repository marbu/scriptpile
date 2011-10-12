#!/bin/bash
# marbu's (crazy) java lib scheme:
# have all jars linked to one dir (~/local/javalib)
# because it is included in CLASSPATH
for i in $(find */ -name '*.jar' -print); do
  if [[ ! -L $(basename "$i") ]]; then
    ln -s $i .
  fi
done
