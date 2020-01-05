#!/bin/bash
TODAY=$(date '+%F')
DFILE=~/tvorba/diary/${TODAY}.md
if [[ ! -s "${DFILE}" ]]; then
  echo -e "## ${TODAY}\n\n" > "${DFILE}"
fi
vim "${DFILE}"
