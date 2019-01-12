#!/bin/bash
# transposes moinmoin wikitable https://moinmo.in/HelpOnMoinWikiSyntax#Tables
# using gnu datamash https://www.gnu.org/software/datamash/
sed 's/^||//;s/||$//;s/||/\t/g' $1 | datamash transpose |  sed 's/\t/||/g;s/^/||/;s/$/||/;'
