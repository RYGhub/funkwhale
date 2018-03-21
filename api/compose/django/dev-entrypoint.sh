#!/bin/bash
set -e
if [ $1 = "pytest" ]; then
    # let pytest.ini handle it
    unset DJANGO_SETTINGS_MODULE
fi
exec "$@"
