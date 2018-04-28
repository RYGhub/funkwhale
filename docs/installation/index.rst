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


Hardware requirements
---------------------

Funkwhale is not especially CPU hungry, unless you're relying heavily
on the transcoding feature (which is basic and unoptimized at the moment).

On a dockerized instance with 2 CPUs and a few active users, the memory footprint is around ~500Mb::

   CONTAINER                   MEM USAGE
   funkwhale_api_1             202.1 MiB
   funkwhale_celerybeat_1      96.52 MiB
   funkwhale_celeryworker_1    168.7 MiB
   funkwhale_postgres_1        22.73 MiB
   funkwhale_redis_1           1.496 MiB

Some users have reported running Funkwhale on Raspberry Pis with a memory
consumption of less than 350MiB.

Thus, Funkwhale should run fine on commodity hardware, small hosting boxes and
Raspberry Pi. We lack real-world exemples of such deployments, so don't hesitate
do give us your feedback (either positive or negative).

Check out :doc:`optimization` for advices on how to tune your instance on small
configurations.

Software requirements
---------------------

Software requirements will vary depending of your installation method. For
Docker-based installations, the only requirement will be an Nginx reverse-proxy
that will expose your instance to the outside world.

If you plan to install your Funkwhale instance without Docker, most of the
dependencies should be available in your distribution's repositories.

.. note::

   Funkwhale works only with Pyhon >= 3.5, as we need support for async/await.
   Older versions of Python are not supported.


Available installation methods
-------------------------------

Docker is the recommended and easiest way to setup your Funkwhale instance.
We also maintain an installation guide for Debian 9.

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

In order to make funkwhale accessible from outside your server and to play nicely with other applications on your machine, you should configure a reverse proxy.

Nginx
^^^^^

Ensure you have a recent version of nginx on your server. On debian-like system, you would have to run the following:

.. code-block:: bash

    apt-get update
    apt-get install nginx

Then, download our sample virtualhost file and proxy conf:

.. parsed-literal::

    curl -L -o /etc/nginx/funkwhale_proxy.conf "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/funkwhale_proxy.conf"
    curl -L -o /etc/nginx/sites-available/funkwhale.conf "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/nginx.conf"
    ln -s /etc/nginx/sites-available/funkwhale.conf /etc/nginx/sites-enabled/

Ensure static assets and proxy pass match your configuration, and check the configuration is valid with ``nginx -t``.
If everything is fine, you can restart your nginx server with ``service nginx restart``.

Apache2
^^^^^^^

.. note::

    Apache2 support is still very recent and the following features
    are not working yet:

    - Websocket (used for real-time updates on Instance timeline)
    - Transcoding of audio files

    Those features are not necessary to use your Funkwhale instance, and
    transcoding in particular is still in alpha-state anyway.

Ensure you have a recent version of apache2 installed on your server.
You'll also need the following dependencies::

   apt install libapache2-mod-xsendfile

Then, download our sample virtualhost file:

.. parsed-literal::

    curl -L -o /etc/apache2/sites-available/funkwhale.conf "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/apache.conf"
    ln -s /etc/apache2/sites-available/funkwhale.conf /etc/apache2/sites-enabled/

You can tweak the configuration file according to your setup, especially the
TLS configuration. Otherwise, defaults, should work if you followed the
installation guide.

Check the configuration is valid with ``apache2ctl configtest``, and once you're
done, load the new configuration with ``service apache2 restart``.

About internal locations
~~~~~~~~~~~~~~~~~~~~~~~~

Music (and other static) files are never served by the app itself, but by the reverse
proxy. This is needed because a webserver is way more efficient at serving
files than a Python process.

However, we do want to ensure users have the right to access music files, and
it can't be done at the proxy's level. To tackle this issue, `we use
nginx's internal directive <http://nginx.org/en/docs/http/ngx_http_core_module.html#internal>`_.

When the API receives a request on its music serving endpoint, it will check
that the user making the request can access the file. Then, it will return an empty
response with a ``X-Accel-Redirect`` header. This header will contain the path
to the file to serve to the user, and will be picked by nginx, but never sent
back to the client.

Using this technique, we can ensure music files are covered by the authentication
and permission policy of your instance, while keeping as much as performance
as possible.
