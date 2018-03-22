Upgrading your funkwhale instance to a newer version
====================================================

.. note::

    Before upgrading your instance, we strongly advise you to make a database
    backup. We're commited to make upgrade as easy and straightforward as possible,
    however, funkwhale is still in development and you'll be safer with a backup.

Reading the release notes
-------------------------

Please take a few minutes to read the :doc:`changelog`: updates should work
similarly from version to version, but some of them may require additional steps.
Those steps would be described in the version release notes.

Upgrade the static files
------------------------

Regardless of your deployment choice (docker/non-docker) the front-end app
is updated separately from the API. This is as simple as downloading
the zip with the static files and extracting it in the correct place.

The following example assume your setup match :ref:`frontend-setup`.

.. parsed-literal::

    # this assumes you want to upgrade to version "|version|"
    export FUNKWHALE_VERSION="|version|"
    cd /srv/funkwhale
    curl -L -o front.zip "https://code.eliotberriot.com/funkwhale/funkwhale/builds/artifacts/$FUNKWHALE_VERSION/download?job=build_front"
    unzip -o front.zip
    rm front.zip

Upgrading the API
-----------------

Docker setup
^^^^^^^^^^^^

If you've followed the setup instructions in :doc:`Docker`, upgrade path is
easy:

.. parsed-literal::

    cd /srv/funkwhale
    # hardcode the targeted version your env file
    # (look for the FUNKWHALE_VERSION variable)
    nano .env
    # Pull the new version containers
    docker-compose pull
    # Apply the database migrations
    docker-compose run --rm api python manage.py migrate
    # Relaunch the containers
    docker-compose up -d

Non-docker setup
^^^^^^^^^^^^^^^^

On non docker-setup, upgrade involves a few more commands. We assume your setup
match what is described in :doc:`debian`:

.. parsed-literal::

    # this assumes you want to upgrade to version "|version|"
    export FUNKWALE_VERSION="|version|"
    cd /srv/funkwhale

    # download more recent API files
    curl -L -o "api-|version|.zip" "https://code.eliotberriot.com/funkwhale/funkwhale/-/jobs/artifacts/|version|/download?job=build_api"
    unzip "api-|version|.zip" -d extracted
    mv extracted/api/* api/
    rm -rf extracted

    # update os dependencies
    sudo api/install_os_dependencies.sh install
    # update python dependencies
    source /srv/funkwhale/load_env
    source /srv/funkwhale/virtualenv/bin/activate
    pip install -r api/requirements.txt

    # apply database migrations
    python api/manage.py migrate
    # collect static files
    python api/manage.py collectstatic --no-input

    # restart the services
    sudo systemctl restart funkwhale.target
