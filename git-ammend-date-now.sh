#!/bin/bash
export GIT_COMMITTER_DATE=$(date +'%b %e %T %Y %z') 
git commit --amend --no-edit --date "${GIT_COMMITTER_DATE}"
