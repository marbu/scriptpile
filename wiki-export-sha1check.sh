#!/bin/bash
# quick and dirty way (hardly optimal :-) to check sha1-base36 checksum of
# wikitext content of wikipedia pages from xml dump file

if [[ $# = 0  || "$1" =~ ^--?h(elp)?$ ]]; then
  echo "Usage: $(basename $0) <list-of-base36hash.wikitext-files>"
  exit
fi

for FILENAME; do
  BASENAME=$(basename "${FILENAME}")
  CHECKSUM_FILENAME=${BASENAME%".wikitext"}
  CHECKSUM_COMPUTED=$(sha1sum "${FILENAME}"|cut -d' ' -f1)

  # convert both checksums into base 10
  VALUE_COMPUTED=$((16#$(tr [a-f] [A-F] <<< ${CHECKSUM_COMPUTED})))
  VALUE_FILENAME=$((36#$(tr [a-z] [A-Z] <<< ${CHECKSUM_FILENAME})))

  # print filename if checksum verification failed
  if [[ ! $VALUE_COMPUTED -eq $VALUE_FILENAME ]]; then
    echo $FILENAME
    FAILURE=1
  fi
done

exit $FAILURE
