#!/bin/bash
# count rpm packages grouped by it's fedora release
# while reporting to stderr any package out of this scheme

rpm -qa | awk '
BEGIN { FS="." }

# ignore packages for gpg keys
/^gpg/ { next }

# count packages by release number
$(NF-1) ~ /^fc/ { rel_count[$(NF-1)]+=1; next }
$(NF-2) ~ /^fc/ { rel_count[$(NF-2)]+=1; next }

# print any other package to stderr
{ print > "/dev/stderr" }

# print the results
END { for (i in rel_count) { printf("%s %5d\n", i, rel_count[i]) } }'
