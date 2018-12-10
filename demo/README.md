# Setup the demo

We assume you want to store the demo data in `/srv/funkwhale-demo`.
This setup requires Docker and docker-compose.

## Create the necessary directories

`mkdir /srv/funkwhale-demo`

## Get some music

You can use your own music (put it in `/usr/share/music`, this is the directory the demo will look into by default).

If you don't have any music, you can use the repository https://dev.funkwhale.audio/funkwhale/catalog, which
requires Git LFS.

## Create an env file

Copy the `env.sample` file to ``/srv/funkwhale-demo/.env`.

Edit the file according to your needs.

## Copy the setup script

Copy the `setup.sh` script to ``/srv/funkwhale-demo/setup.sh`.

Ensure it's executable with `chmod +x setup.sh`.

## Setup your nginx vhost

Setup your reverse proxy for the demo as described in https://docs.funkwhale.audio/installation/index.html#nginx.

This is outside of the scope of this guide, as you will probably want some SSL certificates, however,
ensure you point the vhost configuration to the proper static files:

- `root` should point to `/srv/funkwhale-demo/demo/front/dist`
- `/media` and `/_protected/media` should point to `/srv/funkwhale-demo/demo/data/media/`
- `/staticfiles` should point to `/srv/funkwhale-demo/demo/data/static`

## Launch

Setup the demo:

```
cd /srv/funkwhale-demo
sudo ENV_FILE=/srv/funkwhale-demo/.env ./setup.sh
```

## Automate

You'll probaby want to reset the demo every now and then. You can do that
using a cronjob:

```
sudo crontab -e
# in the crontab, put this:
SHELL=/bin/bash
0 */3 * * * cd /srv/funkwhale-demo && ENV_FILE=/srv/funkwhale-demo/env ./setup.sh > /srv/funkwhale-demo/crontab.log 2>&1
```

This will reset and restart the demo every 3 hours.
