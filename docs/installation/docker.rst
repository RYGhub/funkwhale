Docker installation
===================

Docker is the easiest way to get a Funkwhale instance up and running.

We support two types of Docker deployments:

- :ref:`Mono-container <docker-mono-container>`: all processes live in the same container (database, nginx, redis, etc.). It's easier to deploy and to integrate with container management systems like Portainer. However, it's not possible to scale this type of deployment on multiple servers.
- :ref:`Multi-container <docker-multi-container>`: each process lives in a dedicated container. This setup is more involved but also more flexible and scalable.

.. note::

    We do not distribute Docker images for non-amd64 architectures yet. However, :doc:`you can easily build
    those images yourself following our instructions <non_amd64_architectures>`, and come back to this installation guide once
    the build is over.

.. _docker-mono-container:

Mono-container installation
---------------------------

.. note::

    This installation method was contributed by @thetarkus, at https://github.com/thetarkus/docker-funkwhale

First, ensure you have `Docker <https://docs.docker.com/engine/installation/>`_ installed.

Create the user and the directory:

.. code-block:: shell

    sudo useradd -r -s /usr/bin/nologin -d /srv/funkwhale -m funkwhale
    sudo adduser funkwhale docker
    cd /srv/funkwhale

Log in as the newly created user from now on:

.. code-block:: shell

    sudo -u funkwhale -H bash

Export the version you want to deploy:

.. parsed-literal::

    export FUNKWHALE_VERSION="|version|"

Create an env file to store a few important configuration options:

.. code-block:: shell

    touch .env
    echo "FUNKWHALE_HOSTNAME=yourdomain.funkwhale" >> .env
    echo "FUNKWHALE_PROTOCOL=https" >> .env  # or http
    echo "DJANGO_SECRET_KEY=$(openssl rand -hex 45)" >> .env  # generate and store a secure secret key for your instance

Then start the container:

.. code-block:: shell

    docker run \
        --name=funkwhale \
        --restart=unless-stopped \
        --env-file=/srv/funkwhale/.env \
        -v /srv/funkwhale/data:/data \
        -v /path/to/your/music/dir:/music:ro \
        -e PUID=$UID \
        -e PGID=$GID \
        -p 5000:80 \
        -d \
        funkwhale/all-in-one:$FUNKWHALE_VERSION

.. note::

    - ``-e PUID`` and ``-e PGID`` are optional but useful to prevent permission issues with docker volumes
    - ``-v /path/to/your/music/dir`` should point to a path on your host were is located music you want to import in your Funkwhale instance. You can safely remove the volume if you don't want to import music that way.

Your container should start in the background, and your instance be available at ``yourip:5000`` shortly.

You will need an admin account to login and manage your account, create one using the following command: ``docker exec -it funkwhale manage createsuperuser``

Useful commands:

- You can examine the logs by running ``docker logs -f --tail=50 funkwhale``
- You can start and stop your instance using ``docker start funkwhale`` and ``docker stop funkwhale``, respectively
- To have a better idea of the resource usage of your instance (CPU, memory), run ``docker stats funkwhale``

.. note::

    The container will not pick up changes made in .env file automatically.
    In order to load new configuration, run:

    .. parsed-literal::

        export FUNKWHALE_VERSION="|version|"

    .. code-block:: shell

        # stop and remove the existing container
        docker stop funkwhale
        docker rm funkwhale
        # relaunch a new container
        docker run \
            --name=funkwhale \
            --restart=unless-stopped \
            --env-file=/srv/funkwhale/.env \
            -v /srv/funkwhale/data:/data \
            -v /path/to/your/music/dir:/music:ro \
            -e PUID=$UID \
            -e PGID=$GID \
            -p 5000:80 \
            -d \
            funkwhale/all-in-one:$FUNKWHALE_VERSION

.. _docker-multi-container:

Multi-container installation
----------------------------

First, ensure you have `Docker <https://docs.docker.com/engine/installation/>`_ and `docker-compose <https://docs.docker.com/compose/install/>`_ installed.

Export the version you want to deploy:

.. parsed-literal::

    export FUNKWHALE_VERSION="|version|"

Download the sample docker-compose file:

.. parsed-literal::

    mkdir /srv/funkwhale
    cd /srv/funkwhale
    mkdir nginx
    curl -L -o nginx/funkwhale.template "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/docker.nginx.template"
    curl -L -o nginx/funkwhale_proxy.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/docker.funkwhale_proxy.conf"
    curl -L -o docker-compose.yml "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/docker-compose.yml"

At this point, the architecture of ``/srv/funkwhale``  should look like that:

::

    .
    ├── docker-compose.yml
    └── nginx
        ├── funkwhale_proxy.conf
        └── funkwhale.template

Create your env file:

.. parsed-literal::

    curl -L -o .env "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/env.prod.sample"
    sed -i "s/FUNKWHALE_VERSION=latest/FUNKWHALE_VERSION=$FUNKWHALE_VERSION/" .env
    sudo nano .env

Ensure to edit it to match your needs (this file is heavily commented), in particular ``DJANGO_SECRET_KEY`` and ``FUNKWHALE_HOSTNAME``.
You should take a look at the `configuration reference <https://docs.funkwhale.audio/configuration.html#configuration-reference>`_ for more detailed information regarding each setting.

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
