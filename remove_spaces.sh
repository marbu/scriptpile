#!/bin/bash
# remove spaces from filenames in current directory tree (just an example)

prepare_test()
{
  TESTPATH=$(mktemp -d)
  cd $TESTPATH
  mkdir foo\ bar{0..9}
  for dir in *; do
    touch "$dir"/"f o o "{11..21}
  done
  touch file\ foo{0..9}
}

# this doesn't work (besides ignoring directories):
# find . -name *\ * -print0 | xargs --null -n 1 -I '{}' echo mv '{}' $(echo {} | sed 's/\ //g')
# the sed is called first and since {} expansion is done by xargs later, sed
# would have not effect on the string '{}' itself

do_remove()
{
  find "$1" -depth -name '* *' -print0 \
  | while IFS= read -r -d $'\0' PATHNAME; do
    DIRNAME=$(dirname "$PATHNAME")
    OLDNAME=$(basename "$PATHNAME")
    NEWNAME=$(sed 's/\ //g' <<< "$OLDNAME")
    mv "$PATHNAME" "${DIRNAME}/${NEWNAME}"
  done 
}

#
# main
#

if [[ x$1 = "x--prepare-test" ]]; then
  prepare_test
  echo $TESTPATH
  exit
fi

if [[ x$1 = "x--test" ]]; then
  prepare_test
  do_remove "$TESTPATH"
  echo $TESTPATH
  exit
fi

for i; do
  [[ -d "$i" ]] && do_remove "$i"
done
