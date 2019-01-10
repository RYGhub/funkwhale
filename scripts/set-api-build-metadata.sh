#!/bin/sh -eu
# given a commit hash, will append this to the version number stored
# in api/funkwhale_api/__init__.py

commit=$1
suffix="+git.$commit"
replace="__version__ = \"\1${suffix}\""
file="api/funkwhale_api/__init__.py"
sed -i -E 's@__version__ = \"(.*)\"@'"$replace"'@' $file
