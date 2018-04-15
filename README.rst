Funkwhale
=============

A self-hosted tribute to Grooveshark.com.

LICENSE: BSD

Getting help
------------

We offer various Matrix.org rooms to discuss about funkwhale:

- `#funkwhale:matrix.org <https://riot.im/app/#/room/#funkwhale:matrix.org>`_ for general questions about funkwhale
- `#funkwhale-dev:matrix.org <https://riot.im/app/#/room/#funkwhale-dev:matrix.org>`_ for development-focused discussion

Please join those rooms if you have any questions!

Running the development version
-------------------------------

If you want to fix a bug or implement a feature, you'll need
to run a local, development copy of funkwhale.

We provide a docker based development environment, which should
be both easy to setup and work similarly regardless of your
development machine setup.

Instructions for bare-metal setup will come in the future (Merge requests
are welcome).

Installing docker and docker-compose
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is already cover in the relevant documentations:

- https://docs.docker.com/install/
- https://docs.docker.com/compose/install/

Cloning the project
^^^^^^^^^^^^^^^^^^^

Visit https://code.eliotberriot.com/funkwhale/funkwhale and clone the repository using SSH or HTTPS. Exemple using SSH::

    git clone ssh://git@code.eliotberriot.com:2222/funkwhale/funkwhale.git
    cd funkwhale


A note about branches
^^^^^^^^^^^^^^^^^^^^^

Next release development occurs on the "develop" branch, and releases are made on the "master" branch. Therefor, when submitting Merge Requests, ensure you are merging on the develop branch.


Working with docker
^^^^^^^^^^^^^^^^^^^

In developpement, we use the docker-compose file named ``dev.yml``, and this is why all our docker-compose commands will look like this::

    docker-compose -f dev.yml logs

If you do not want to add the ``-f dev.yml`` snippet everytime, you can run this command before starting your work::

    export COMPOSE_FILE=dev.yml


Building the containers
^^^^^^^^^^^^^^^^^^^^^^^

On your initial clone, or if there have been some changes in the
app dependencies, you will have to rebuild your containers. This is done
via the following command::

    docker-compose -f dev.yml build


Creating your env file
^^^^^^^^^^^^^^^^^^^^^^

We provide a working .env.dev configuration file that is suitable for
development. However, to enable customization on your machine, you should
also create a .env file that will hold your personal environment
variables (those will not be commited to the project).

Create it like this::

    touch .env


Database management
^^^^^^^^^^^^^^^^^^^

To setup funkwhale's database schema, run this::

    docker-compose -f dev.yml run --rm api python manage.py migrate

This will create all the tables needed for the API to run proprely.
You will also need to run this whenever changes are made on the database
schema.

It is safe to run this command multiple times, so you can run it whenever
you fetch develop.


Development data
^^^^^^^^^^^^^^^^

You'll need at least an admin user and some artists/tracks/albums to work
locally.

Create an admin user with the following command::

    docker-compose -f dev.yml run --rm api python manage.py createsuperuser

Injecting fake data is done by running the fllowing script::

    artists=25
    command="from funkwhale_api.music import fake_data; fake_data.create_data($artists)"
    echo $command | docker-compose -f dev.yml run --rm api python manage.py shell -i python

The previous command will create 25 artists with random albums, tracks
and metadata.


Launch all services
^^^^^^^^^^^^^^^^^^^

Then you can run everything with::

    docker-compose -f dev.yml up

This will launch all services, and output the logs in your current terminal window.
If you prefer to launch them in the background instead, use the ``-d`` flag, and access the logs when you need it via ``docker-compose -f dev.yml logs --tail=50 --follow``.

Once everything is up, you can access the various funkwhale's components:

- The Vue webapp, on http://localhost:8080
- The API, on http://localhost:8080/api/v1/
- The django admin, on http://localhost:8080/api/admin/


Running API tests
^^^^^^^^^^^^^^^^^

To run the pytest test suite, use the following command::

    docker-compose -f dev.yml run --rm api pytest

This is regular pytest, so you can use any arguments/options that pytest usually accept::

    # get some help
    docker-compose -f dev.yml run --rm api pytest -h
    # Stop on first failure
    docker-compose -f dev.yml run --rm api pytest -x
    # Run a specific test file
    docker-compose -f dev.yml run --rm api pytest tests/test_acoustid.py


Running front-end tests
^^^^^^^^^^^^^^^^^^^^^^^

To run the front-end test suite, use the following command::

    docker-compose -f dev.yml run --rm front yarn run unit

We also support a "watch and test" mode were we continually relaunch
tests when changes are recorded on the file system::

    docker-compose -f dev.yml run --rm front yarn run unit-watch

The latter is especially useful when you are debugging failing tests.

.. note::

    The front-end test suite coverage is still pretty low


Stopping everything
^^^^^^^^^^^^^^^^^^^

Once you're down with your work, you can stop running containers, if any, with::

    docker-compose -f dev.yml stop


Removing everything
^^^^^^^^^^^^^^^^^^^

If you want to wipe your development environment completely (e.g. if you want to start over from scratch), just run::

    docker-compose -f dev.yml down -v

This will wipe your containers and data, so please be careful before running it.

You can keep your data by removing the ``-v`` flag.


Typical workflow for a merge request
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0. Fork the project if you did not already or if you do not have access to the main repository
1. Checkout the development branch and pull most recent changes: ``git checkout develop && git pull``
2. Create a dedicated branch for your work ``42-awesome-fix``. It is good practice to prefix your branch name with the ID of the issue you are solving.
3. Work on your stuff
4. Commit small, atomic changes to make it easier to review your contribution
5. Add a changelog fragment to summarize your changes: ``echo "Implemented awesome stuff (#42)" > changes/changelog.d/42.feature"``
6. Push your branch
7. Create your merge request
8. Take a step back and enjoy, we're really grateful you did all of this and took the time to contribute!


Working with federation locally
-------------------------------

To achieve that, you'll need:

1. to update your dns resolver to resolve all your .dev hostnames locally
2. a reverse proxy (such as traefik) to catch those .dev requests and
   and with https certificate
3. two instances (or more) running locally, following the regular dev setup

Resolve .dev names locally
^^^^^^^^^^^^^^^^^^^^^^^^^^

If you use dnsmasq, this is as simple as doing::

    echo "address=/test/172.17.0.1" | sudo tee /etc/dnsmasq.d/test.conf
    sudo systemctl restart dnsmasq

If you use NetworkManager with dnsmasq integration, use this instead::

    echo "address=/test/172.17.0.1" | sudo tee /etc/NetworkManager/dnsmasq.d/test.conf
    sudo systemctl restart NetworkManager

Add wildcard certificate to the trusted certificates
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Simply copy bundled certificates::

    sudo cp docker/ssl/test.crt /usr/local/share/ca-certificates/
    sudo update-ca-certificates

This certificate is a wildcard for ``*.funkwhale.test``

Run a reverse proxy for your instances
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


Crete docker network
^^^^^^^^^^^^^^^^^^^^

Create the federation network::

    docker network create federation

Launch everything
^^^^^^^^^^^^^^^^^

Launch the traefik proxy::

    docker-compose -f docker/traefik.yml up -d

Then, in separate terminals, you can setup as many different instances as you
need::

    export COMPOSE_PROJECT_NAME=node2
    docker-compose -f dev.yml run --rm api python manage.py migrate
    docker-compose -f dev.yml run --rm api python manage.py createsuperuser
    docker-compose -f dev.yml up nginx api front

Note that by default, if you don't export the COMPOSE_PROJECT_NAME,
we will default to node1 as the name of your instance.

Assuming your project name is ``node1``, your server will be reachable
at ``https://node1.funkwhale.test/``. Not that you'll have to trust
the SSL Certificate as it's self signed.

When working on federation with traefik, ensure you have this in your ``env``::

    # This will ensure we don't bind any port on the host, and thus enable
    # multiple instances of funkwhale to be spawned concurrently.
    WEBPACK_DEVSERVER_PORT_BINDING=
    # This disable certificate verification
    EXTERNAL_REQUESTS_VERIFY_SSL=false
    # this ensure you don't have incorrect urls pointing to http resources
    FUNKWHALE_PROTOCOL=https
