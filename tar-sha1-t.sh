#!/bin/bash
# simple "tar --to-command" script to list sha1 checksum of archived files
# without extracting them somewhere, see example usage:
#
# $ tar xf foo.tar.gz --to-command=~/bin/tar-sha1-t.sh
# 384dcab2b0e67e940406d1bbfd1b083c61319ce4 foobar.png
# e1c272d5abe7d339c4047d76294e7400c31e63b4 README
#
# See also: man tar, https://unix.stackexchange.com/questions/303667/

echo -n $(sha1sum) | sed 's/ .*$//'
echo " $TAR_FILENAME"
