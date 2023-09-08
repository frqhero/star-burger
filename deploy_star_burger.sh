#!/bin/bash
set -e
if [ -z ${ROLLBAR_TOKEN} ]; then
    echo "ROLLBAR_TOKEN env var not found"
    exit 1
fi

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
venv/bin/python manage.py migrate --noinput

echo "~~~restart systemd~~~"
systemctl restart star_burger.service
systemctl restart postgresql.service

echo "~~~inform rollbar~~~"
sha=$(git rev-parse HEAD)
curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header "X-Rollbar-Access-Token: ${ROLLBAR_TOKEN}" \
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
