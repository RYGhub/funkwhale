#!/bin/bash -eux
python /app/manage.py collectstatic --noinput
/usr/local/bin/daphne -b 0.0.0.0 -p 5000 config.asgi:application --proxy-headers
