#! /bin/bash

echo "Loading demo data..."

python manage.py migrate --noinput

echo "Creating demo user..."

cat demo/demo-user.py | python manage.py shell --plain

echo "Importing demo tracks..."

python manage.py import_files "/music/**/*.ogg" --recursive --noinput
