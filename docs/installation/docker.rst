Docker installation
====================

Docker is the easiest way to get a Funkwhale instance up and running.

First, ensure you have `Docker <https://docs.docker.com/engine/installation/>`_ and `docker-compose <https://github.com/docker/compose/releases>`_ installed.

Download the sample docker-compose file:

.. parsed-literal::

    cd /srv/funkwhale
    mkdir nginx
    curl -L -o nginx/funkwhale.template "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/docker.nginx.template"
    curl -L -o nginx/funkwhale_proxy.conf "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/funkwhale_proxy.conf"
    curl -L -o docker-compose.yml "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/docker-compose.yml"

Create your env file:

.. parsed-literal::

    export FUNKWHALE_VERSION="|version|"
    curl -L -o .env "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/env.prod.sample"
    sed -i "s/FUNKWHALE_VERSION=latest/FUNKWHALE_VERSION=$FUNKWHALE_VERSION/" .env

Ensure to edit it to match your needs (this file is heavily commented)

Then, you should be able to pull the required images:

.. code-block:: bash

    docker-compose pull

Run the database container and the initial migrations:

.. code-block:: bash

    docker-compose up -d postgres
    docker-compose run --rm api python manage.py migrate

.. warning::

    You may sometimes get the following warning while applying migrations::

        "Your models have changes that are not yet reflected in a migration, and so won't be applied."

    This is a warning, not an error, and it can be safely ignored.
    Never run the ``makemigrations`` command yourself.

Create your admin user:

.. code-block:: bash

    docker-compose run --rm api python manage.py createsuperuser

Then launch the whole thing:

.. code-block:: bash

    docker-compose up -d

Now, you just need to configure your :ref:`reverse-proxy <reverse-proxy-setup>`. Don't worry, it's quite easy.

About music acquisition
-----------------------

If you want to :doc:`import music located on the server </importing-music>`, you can put it in the ``data/music`` directory and it will become readable by the importer.
