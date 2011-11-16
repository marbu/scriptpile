#!/bin/bash
# convert various 'office files' to pdf
# using unoconv (libreoffice daemon mode)

show_help() {
  echo -e "Usage: pdf-export list_of_files"
}

convert_to_pdf() {
  FILE="$1"
  NAME=$(sed 's/\(.*\)\..*$/\1/' <<< "$FILE")
  if [[ ! -e "$FILE" ]]; then
    echo "$FILE doesn't exist" >&2
    $DEBUG return
  fi
  if [[ -e "${NAME}.pdf" ]]; then
    echo "already converted: $FILE" >&2
    $DEBUG return
  fi
  echo "converting $FILE" >&2
  $DEBUG unoconv -f pdf "$FILE"
}

#
# main
#

if [[ $# = 0 ]]; then
  show_help
  exit
fi

case $1 in
  -d)         DEBUG=echo; shift;;
  -h|--help)  show_help; exit;;
esac

for i; do
  convert_to_pdf "$i"
done
