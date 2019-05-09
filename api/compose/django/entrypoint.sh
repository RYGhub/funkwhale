#!/bin/sh
set -e
# This entrypoint is used to play nicely with the current cookiecutter configuration.
# Since docker-compose relies heavily on environment variables itself for configuration, we'd have to define multiple
# environment variables just to support cookiecutter out of the box. That makes no sense, so this little entrypoint
# does all this for us.
export CACHE_URL=${CACHE_URL:="redis://redis:6379/0"}

if [ -z "$DATABASE_URL" ]; then
  # the official postgres image uses 'postgres' as default user if not set explictly.
  if [ -z "$POSTGRES_ENV_POSTGRES_USER" ]; then
    export POSTGRES_ENV_POSTGRES_USER=postgres
  fi
  export DATABASE_URL=postgres://$POSTGRES_ENV_POSTGRES_USER:$POSTGRES_ENV_POSTGRES_PASSWORD@postgres:5432/$POSTGRES_ENV_POSTGRES_USER
fi

if [ -z "$CELERY_BROKER_URL" ]; then
  export CELERY_BROKER_URL=$CACHE_URL
fi

# we copy the frontend files, if any so we can serve them from the outside
if [ -d "frontend" ]; then
  mkdir -p /frontend
  cp -r frontend/* /frontend/
  export FUNKWHALE_SPA_HTML_ROOT=/frontend/index.html
fi
exec "$@"
