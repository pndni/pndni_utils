#!/bin/bash

set -e
set -u
\unalias -a
status=0

dest="$1"
shift
cp -r --backup=numbered --target-directory "$dest" "$@"
for f in $(find "$dest" -regex '.*~[0-9][0-9]*~$')
do
    if cmp ${f%\.~[0-9]*~} $f
    then
        rm $f
    else
	status=1
    fi
done
exit $status
