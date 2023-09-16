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

echo "~~docker compose down~~"
docker compose -f prod.yaml down

echo "~~docker compose up~~"
docker compose -f prod.yaml up --build -d

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
