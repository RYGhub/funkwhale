Upgrading your Funkwhale instance to a newer version
====================================================

.. note::

    Before upgrading your instance, we strongly advise you to make at least a database backup. Ideally, you should make a full backup, including
    the database and the media files.

    We're commited to make upgrade as easy and straightforward as possible,
    however, Funkwhale is still in development and you'll be safer with a backup.


Reading the release notes
-------------------------

Please take a few minutes to read the :doc:`changelog`: updates should work
similarly from version to version, but some of them may require additional steps.
Those steps would be described in the version release notes.


Insights about new versions
---------------------------

Some versions may be bigger than usual, and we'll try to detail the changes
when possible.

.. toctree::
   :maxdepth: 1

   0.17


Docker setup
------------

If you've followed the setup instructions in :doc:`Docker`, upgrade path is
easy:

.. parsed-literal::

    cd /srv/funkwhale
    # hardcode the targeted version your env file
    # (look for the FUNKWHALE_VERSION variable)
    nano .env
    # Load your environment variables
    source .env
    # Download newest nginx configuration file
    curl -L -o nginx/funkwhale.template "https://code.eliotberriot.com/funkwhale/funkwhale/raw/develop/deploy/docker.nginx.template"
    curl -L -o nginx/funkwhale_proxy.conf "https://code.eliotberriot.com/funkwhale/funkwhale/raw/develop/deploy/funkwhale_proxy.conf"
    # Pull the new version containers
    docker-compose pull
    # Apply the database migrations
    docker-compose run --rm api python manage.py migrate
    # Relaunch the containers
    docker-compose up -d

.. warning::

    You may sometimes get the following warning while applying migrations::

        "Your models have changes that are not yet reflected in a migration, and so won't be applied."

    This is a warning, not an error, and it can be safely ignored.
    Never run the ``makemigrations`` command yourself.


Non-docker setup
----------------

Upgrade the static files
^^^^^^^^^^^^^^^^^^^^^^^^

On non-docker setups, the front-end app
is updated separately from the API. This is as simple as downloading
the zip with the static files and extracting it in the correct place.

The following example assume your setup match :ref:`frontend-setup`.

.. parsed-literal::

    # this assumes you want to upgrade to version "|version|"
    export FUNKWHALE_VERSION="|version|"
    cd /srv/funkwhale
    sudo -u funkwhale curl -L -o front.zip "https://code.eliotberriot.com/funkwhale/funkwhale/builds/artifacts/$FUNKWHALE_VERSION/download?job=build_front"
    sudo -u funkwhale unzip -o front.zip
    sudo -u funkwhale rm front.zip

Upgrading the API
^^^^^^^^^^^^^^^^^

On non-docker, upgrade involves a few more commands. We assume your setup
match what is described in :doc:`/installation/debian`:

.. parsed-literal::

    # this assumes you want to upgrade to version "|version|"
    export FUNKWHALE_VERSION="|version|"
    cd /srv/funkwhale

    # download more recent API files
    sudo -u funkwhale curl -L -o "api-$FUNKWHALE_VERSION.zip" "https://code.eliotberriot.com/funkwhale/funkwhale/-/jobs/artifacts/$FUNKWHALE_VERSION/download?job=build_api"
    sudo -u funkwhale unzip "api-$FUNKWHALE_VERSION.zip" -d extracted
    sudo -u funkwhale rm -rf api/ && mv extracted/api .
    sudo -u funkwhale rm -rf extracted

    # update os dependencies
    sudo api/install_os_dependencies.sh install
    sudo -u funkwhale -E /srv/funkwhale/virtualenv/bin/pip install -r api/requirements.txt

    # collect static files
    sudo -u funkwhale -E /srv/funkwhale/virtualenv/bin/python api/manage.py collectstatic --no-input

    # stop the services
    sudo systemctl stop funkwhale.target

    # apply database migrations
    sudo -u funkwhale -E /srv/funkwhale/virtualenv/bin/python api/manage.py migrate

    # restart the services
    sudo systemctl start funkwhale.target

.. warning::

    You may sometimes get the following warning while applying migrations::

        "Your models have changes that are not yet reflected in a migration, and so won't be applied."

    This is a warning, not an error, and it can be safely ignored.
    Never run the ``makemigrations`` command yourself.
