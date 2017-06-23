Funkwhale
=============

A self-hosted tribute to Grooveshark.com.

LICENSE: BSD

Setting up a development environment (docker)
----------------------------------------------

First of all, pull the repository.

Then, pull and build all the containers::

    docker-compose -f dev.yml build
    docker-compose -f dev.yml pull


API setup
^^^^^^^^^^

You'll have apply database migrations::

    docker-compose -f dev.yml run celeryworker python manage.py migrate

And to create an admin user::

    docker-compose -f dev.yml run celeryworker python manage.py createsuperuser


Launch all services
^^^^^^^^^^^^^^^^^^^

Then you can run everything with::

    docker-compose up

The API server will be accessible at http://localhost:6001, and the front-end at http://localhost:8080.

Running API tests
------------------

Everything is managed using docker and docker-compose, just run::

    ./api/runtests

This bash script invoke `python manage.py test` in a docker container under the hood, so you can use
traditional django test arguments and options, such as::

    ./api/runtests funkwhale_api.music   # run a specific app test
