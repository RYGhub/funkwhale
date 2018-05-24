#!/bin/bash -eux
version="develop"
music_path="/usr/share/music"
demo_path="/srv/funkwhale-demo/demo"

echo 'Cleaning everything...'
cd $demo_path
/usr/local/bin/docker-compose down -v || echo 'Nothing to stop'
rm -rf /srv/funkwhale-demo/demo/*
mkdir -p $demo_path
echo 'Downloading demo files...'
curl -L -o docker-compose.yml "https://code.eliotberriot.com/funkwhale/funkwhale/raw/$version/deploy/docker-compose.yml"
curl -L -o .env "https://code.eliotberriot.com/funkwhale/funkwhale/raw/$version/deploy/env.prod.sample"

mkdir data/
cp -r $music_path data/music

curl -L -o front.zip "https://code.eliotberriot.com/funkwhale/funkwhale/-/jobs/artifacts/$version/download?job=build_front"
unzip front.zip

echo "FUNKWHALE_URL=https://demo.funkwhale.audio/" >> .env
echo "DJANGO_SECRET_KEY=demo" >> .env
echo "DJANGO_ALLOWED_HOSTS=demo.funkwhale.audio" >> .env
echo "FUNKWHALE_VERSION=$version" >> .env
echo "FUNKWHALE_API_PORT=5001" >> .env
/usr/local/bin/docker-compose pull
/usr/local/bin/docker-compose up -d postgres redis
sleep 5
/usr/local/bin/docker-compose run --rm api demo/load-demo-data.sh
/usr/local/bin/docker-compose up -d
