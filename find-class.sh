#!/bin/bash
# find jar file which contains given java class (not much efficient though)
# output has form: full_class_name path_of_jar_file

# example of use:
# rpm -qa '*hadoop*' | xargs rpm -ql | ./find-class.sh YarnApplicationState
# ./find-class.sh /usr/share/hadoop YarnApplicationState

show_help()
{
  echo "Usage: $(basename $0) [options] <path> <class-name>"
}

classgrep()
{
  while read JARFILE; do
    if [[ ! $JARFILE =~ \.jar$ ]]; then
      continue
    fi
    jar -tvf "${JARFILE}" | grep "${CLASS}" > /dev/null
    FOUND=$?
    if [[ ${FOUND} -eq 0 ]]; then
      jar -tvf "${JARFILE}" \
      | sed -n "/${CLASS}/s/.*\ \(.*\)/\1/p" \
      | sed 's!/!.!g;s/\.class$//' \
      | xargs -I'{}' echo '{}' "${JARFILE}"
    fi
  done;
}

find_classgrep()
{
  WHERE="$1"
  CLASS="$2"
  find "${WHERE}" -name '*.jar' | classgrep
}

read_classgrep()
{
  CLASS="$1"
  classgrep
}

#
# main
#

if [[ $# = 0  || "$1" =~ ^--?h(elp)?$ ]]; then
  show_help
  exit
fi

# debug mode
if [[ $1 = "-d" ]]; then
  DEBUG=echo
  shift
fi

if [[ $# = 1 ]]; then
  # expects list of jar files on stdin, arg1 is class name
  read_classgrep "$1"
elif [[ $# = 2 ]]; then
  # arg1 is path (where to look for jar files), arg2 is class name
  find_classgrep "$1" "$2"
else
  show_help
  exit 1
fi
