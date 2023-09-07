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

echo "~~~inform rollbar~~~"
sha=$(git rev-parse HEAD)
curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header 'X-Rollbar-Access-Token: af7e5b6ed3f343fab5b4205e1ba0a24f' \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "environment": "production",
  "revision": "'${sha}'"
}
'

echo "~~~success! deployment done~~~"

cd $working_directory
