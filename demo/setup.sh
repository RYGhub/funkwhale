#!/bin/bash -eux
version=${VERSION:-develop}
music_path=${MUSIC_PATH:-/usr/share/music}
demo_path=${DEMO_PATH:-/srv/funkwhale-demo/demo}
env_file=${ENV_FILE}
echo 'Cleaning everything...'
mkdir -p $demo_path
cd $demo_path
/usr/local/bin/docker-compose down -v || echo 'Nothing to stop'
sudo rm -rf $demo_path/*
mkdir -p $demo_path
echo 'Downloading demo files...'
curl -L -o docker-compose.yml "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/$version/deploy/docker-compose.yml"
curl -L -o .env "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/$version/deploy/env.prod.sample"
mkdir nginx
curl -L -o nginx/funkwhale.template "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/$version/deploy/docker.nginx.template"
curl -L -o nginx/funkwhale_proxy.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/$version/deploy/funkwhale_proxy.conf"

mkdir data/
curl -L -o front.zip "https://dev.funkwhale.audio/funkwhale/funkwhale/-/jobs/artifacts/$version/download?job=build_front"
unzip front.zip

cat $env_file >> .env
echo "FUNKWHALE_VERSION=$version" >> .env
echo "MUSIC_DIRECTORY_SERVE_PATH=$music_path" >> .env
echo "MUSIC_DIRECTORY_PATH=$music_path" >> .env
echo "MEDIA_ROOT=$demo_path/data/media/" >> .env
echo "STATIC_ROOT=$demo_path/data/static/" >> .env
echo "FUNKWHALE_FRONTEND_PATH=$demo_path/front/dist/" >> .env

# /usr/local/bin/docker-compose pull
/usr/local/bin/docker-compose up -d postgres redis
sleep 5
cat .env
cat <<EOF | /usr/local/bin/docker-compose run --rm api python manage.py shell -i python
import subprocess
subprocess.call("pip install factory-boy", shell=True)

from django.core.management import call_command

call_command("migrate", interactive=False)

from funkwhale_api.users.models import User

print("Creating dummy user")
u = User.objects.create(email="demo@demo.com", username="demo", is_staff=True, is_superuser=True, privacy_level="everyone")
u.set_password("demo")
u.subsonic_api_token = "demo"
u.save()
actor = u.create_actor()
library = actor.libraries.create(name='Demo library', privacy_level='everyone')

from funkwhale_api.common import preferences

manager = preferences.global_preferences_registry.manager()
manager['common__api_authentication_required'] = False
manager['instance__name'] = "Login: demo / password: demo"

paths = [
    "$music_path/**/*.ogg",
    "$music_path/**/*.mp3",
    "$music_path/**/*.flac",
]
print(paths)
call_command("import_files", str(library.uuid), *paths, username="demo", recursive=True, interactive=False)

print('Creating some dummy data...')

import random
import datetime
from funkwhale_api.music.models import Album, Track
from funkwhale_api.history.factories import ListeningFactory
from funkwhale_api.favorites.factories import TrackFavorite as TrackFavoriteFactory
from funkwhale_api.users.factories import UserFactory
from funkwhale_api.playlists.factories import PlaylistFactory

users = UserFactory.create_batch(size=15, privacy_level="everyone", with_actor=True)
available_tracks = list(Track.objects.all())
available_albums = list(Album.objects.all())

def get_random_datetime():
    from django.utils import timezone
    import datetime
    import random
    now = timezone.now()
    return now - datetime.timedelta(seconds=random.randint(1, 3600 * 24 * 7))

print('Updating album dates to have random sorting...')
for album in available_albums:
    album.creation_date = get_random_datetime()
    album.save(update_fields=['creation_date'])

for i in range(30):
    print('Creating playlist {}'.format(i))
    playlist = PlaylistFactory(user=random.choice(users), privacy_level="everyone", creation_date=get_random_datetime())
    tracks = set()

    for i in range(random.randint(5, 35)):
        tracks.add(random.choice(available_tracks))

    playlist.insert_many(tracks)

for user in users:
    for i in range(random.randint(5, 35)):
        print('Adding favorite {} for user {}'.format(i, user.username))
        try:
            TrackFavoriteFactory(user=user, track=random.choice(available_tracks), creation_date=get_random_datetime())
        except:
            pass
    for i in range(random.randint(5, 35)):
        print('Adding listening {} for user {}'.format(i, user.username))
        try:
            ListeningFactory(user=user, track=random.choice(available_tracks), creation_date=get_random_datetime())
        except:
            pass
EOF

chmod 777 -R front
/usr/local/bin/docker-compose up -d
