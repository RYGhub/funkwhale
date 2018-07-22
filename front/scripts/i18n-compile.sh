#!/bin/bash -eux
locales=$(tail -n +2 src/locales.js | sed -e 's/export default //' | jq '.locales[].code' | xargs echo)
find locales -name '*.po' | xargs $(yarn bin gettext-extract)/gettext-compile --output src/translations.json
