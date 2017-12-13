Installation
=============

Project architecture
--------------------

The project relies on the following components and services to work:

- A web application server (Python/Django/Gunicorn)
- A PostgreSQL database to store application data
- A redis server to store cache and tasks data
- A celery worker to run asynchronouse tasks (such as music import)
- A celery scheduler to run recurrent tasks

Available installation methods
-------------------------------

.. toctree::
   :maxdepth: 1

   external_dependencies
   debian
   docker
   systemd


.. _frontend-setup:

Frontend setup
---------------

.. note::

    You do not need to do this if you are deploying using Docker, as frontend files
    are already included in the funkwhale docker image.

Files for the web frontend are purely static and can simply be downloaded, unzipped and served from any webserver:

.. parsed-literal::

    cd /srv/funkwhale
    curl -L -o front.zip "https://code.eliotberriot.com/funkwhale/funkwhale/builds/artifacts/|version|/download?job=build_front"
    unzip front.zip

.. _reverse-proxy-setup:

Reverse proxy
--------------

In order to make funkwhale accessible from outside your server and to play nicely with other applications on your machine, you should configure a reverse proxy. At the moment, we only have documentation for nginx, if you know how to implement the same thing for apache, you're welcome.

Nginx
^^^^^

Ensure you have a recent version of nginx on your server. On debian-like system, you would have to run the following:

.. code-block:: bash

    apt-get update
    apt-get install nginx

Then, download our sample virtualhost file:

.. parsed-literal::

    curl -L -o /etc/nginx/sites-enabled/funkwhale.conf "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/nginx.conf"

Ensure static assets and proxy pass match your configuration, and check the configuration is valid with ``nginx -t``. If everything is fine, you can restart your nginx server with ``service nginx restart``.
