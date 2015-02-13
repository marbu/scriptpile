#!/bin/bash
echo -n "u48" \
| sha1sum \
| head -c3 \
| sed 's!.!\u&!' \
| sed 's/$/!\n/'
