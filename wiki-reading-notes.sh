#!/bin/bash

# hardcoded configuration, yeah
WIKIDIR=~/tvorba/wiki
NOTES=reading-notes/articles.page
SCRIPTNAME=$(basename "$0")

show_help()
{
  echo -e "${SCRIPTNAME}: edit reading notes in a personal wiki\n"
  echo "Usage: ${SCRIPTNAME} [-h] <url>"
  echo """
  url  creates new section for the given url, if needed
  -g   grep mode, just search for given url
  -h   show help (this message)"""
}

cd "${WIKIDIR}" || { echo "${SCRIPTNAME}: WIKIDIR not found"; exit 1; }

if [[ $1 = "-h" || $1 = "help" ]]; then
  show_help
  exit
fi

if [[ $1 = "-g" ]]; then
  shift
  rg -n "$1" "${NOTES}"
  exit
fi

if [[ $1 =~ ^http.* ]]; then
  URL=$1
  # try to find the url in the notes first
  MATCH=$(grep -n "${URL}" "${NOTES}")
  if [[ $? -eq 0 ]]; then
    MATCH_LINE=$(cut -d: -f1 <<< "${MATCH}")
  else
    # TODO: fetch title of the page
    TITLE=TODO
    {
      echo "* ${TITLE}";
      echo "- [[${URL}]]";
      echo "- added $(date -Idate)";
    } >> "${NOTES}"
  fi
fi

# open the file on the machined line, or at the end
vim +"${MATCH_LINE}" "${NOTES}"
git add "${NOTES}"
git commit -m "reading notes"
