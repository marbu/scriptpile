#!/bin/bash

SCRIPTNAME=$(basename "$0")

# defaults
: "${WIKIDIR:=~/tvorba/wiki}"
WIKIPAGE=reading-notes/articles.page

show_help()
{
  echo -e "${SCRIPTNAME}: edit reading notes in a personal wiki\n"
  echo "Usage: ${SCRIPTNAME} [-h] <url>"
  echo """
  url  creates new section for the given url, if needed
  -p   name of the wiki page (using \"${WIKIPAGE%.page}\" if not specified)
  -g   grep mode, just search for given url
  -h   show help (this message)"""
}

cd_wikidir()
{
  if ! cd "${WIKIDIR}"; then
    echo "${SCRIPTNAME}: WIKIDIR not found" >&2
    exit 1
  fi
}

grep_notes()
{
  cd_wikidir
  rg -n "$1" "${WIKIPAGE}"
}

init_notes()
{
  WIKIPAGE=$1
  WIKINAME=$(basename "${1%.page}")
  PAGEDIRNAME=$(dirname "$1")
  mkdir -p "${PAGEDIRNAME}"
  {
    echo "---";
    echo "format: org";
    echo "categories: reading-notes";
    echo "title: ${WIKINAME} Reading Notes";
    echo "...";
  } >> "${WIKIPAGE}"
}

find_url()
{
  URL=$1
  # try to find the url in the notes first
  MATCH=$(grep -n "${URL}" "${WIKIPAGE}")
  if [[ $? -eq 0 ]]; then
    MATCH_LINE=$(cut -d: -f1 <<< "${MATCH}")
  else
    # TODO: fetch title of the page
    TITLE=TODO
    {
      echo "* ${TITLE}";
      echo "- [[${URL}]]";
      echo "- added $(date -Idate)";
    } >> "${WIKIPAGE}"
  fi
}

edit_notes()
{
  # open the file on the machined line, or at the end
  vim +"${MATCH_LINE}" "${WIKIPAGE}"
  git add "${WIKIPAGE}"
  git commit -m "reading notes"
}

#
# main
#

if [[ $1 = "help" ]]; then
  show_help
  exit
fi

while getopts "p:g:h" OPT; do
  case $OPT in
  g)  grep_notes "$OPTARG";
      exit;;
  p)  WIKIPAGE=${OPTARG}.page;;
  h)  show_help;
      exit;;
  *)  echo;
	  show_help;
      exit 1;;
  esac
done

shift $((OPTIND-1))

cd_wikidir

# create wiki page for the notes if it doesn't exist
if [[ ! -f "${WIKIPAGE}" ]]; then
  init_notes "${WIKIPAGE}"
fi

if [[ $1 =~ ^http.* ]]; then
  find_url "$1"
fi

edit_notes
