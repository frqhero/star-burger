#!/bin/bash
set -e
working_directory=$(pwd)

echo "~~~cd to /opt/star-burger~~~"
cd /opt/star-burger/

echo "~~~git pull~~~"
git pull

echo "~~~install python libraries~~~"
venv/bin/pip install -r requirements.txt

echo "~~~install node libraries~~~"
npm ci --dev

echo "~~~build js code~~~"
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "~~~collect django static~~~"
venv/bin/python manage.py collectstatic --noinput

echo "~~~django migrate~~~"
venv/bin/python manage.py migrate

echo "~~~restart systemd~~~"
systemctl restart star_burger.service
systemctl restart postgresql.service

echo "~~~success! deployment done~~~"

cd $working_directory
