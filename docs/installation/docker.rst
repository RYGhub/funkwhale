Docker installation
====================

Docker is the easiest way to get a funkwhale instance up and running.

First, ensure you have `Docker <https://docs.docker.com/engine/installation/>`_ and `docker-compose <https://github.com/docker/compose/releases>`_ installed.

Download the sample docker-compose file:

.. code-block:: bash

    mkdir -p /srv/funkwhale
    cd /srv/funkwhale
    curl -L -o docker-compose.yml "https://code.eliotberriot.com/funkwhale/funkwhale/raw/master/deploy/docker-compose.yml"

Create your env file:

.. code-block:: bash

    curl -L -o .env "https://code.eliotberriot.com/funkwhale/funkwhale/raw/master/deploy/env.prod.sample"

Ensure to edit it to match your needs (this file is heavily commented)

Then, you should be able to pull the required images:

.. code-block:: bash

    docker-compose pull

Run the database container and the initial migrations:

.. code-block:: bash

    docker-compose up -d postgres
    docker-compose run --rm api python manage.py migrate

Create your admin user:

.. code-block:: bash

    docker-compose run --rm api python manage.py createsuperuser

Then launch the whole thing:

.. code-block:: bash

    docker-compose up -d

Now, you just need to setup the :ref:`frontend files <frontend-setup>`, and configure your :ref:`reverse-proxy <reverse-proxy-setup>`. Don't worry, it's quite easy.

About music acquisition
-----------------------

If you want to :doc:`import music located on the server </importing-music>`, you can put it in the ``data/music`` directory and it will become readable by the importer.
