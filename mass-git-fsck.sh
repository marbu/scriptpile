#!/bin/bash
find . -name '.git' -print0 | while IFS= read -r -d $'\0' GITDIR; do
  echo "fsck ${GITDIR}"
  git --git-dir="${GITDIR}" fsck || echo "fsck failed for ${GITDIR}"
done
