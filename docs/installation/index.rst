Installation
=============

Project architecture
--------------------

The project relies on the following components and services to work:

- A web application server (Python/Django/Gunicorn)
- A PostgreSQL database to store application data
- A redis server to store cache and tasks data
- A celery worker to run asynchronous tasks (such as music import)
- A celery scheduler to run recurrent tasks
- A `ntp-synced clock <https://wiki.debian.org/NTP>`_ to ensure federation is working seamlessly

.. note::

    The synced clock is needed for federation purpose, to assess
    the validity of incoming requests.


Hardware requirements
---------------------

Funkwhale is not especially CPU hungry. On a dockerized instance with 2 CPUs
and a few active users, the memory footprint is around ~500Mb::

   CONTAINER                   MEM USAGE
   funkwhale_api_1             202.1 MiB
   funkwhale_celerybeat_1      96.52 MiB
   funkwhale_celeryworker_1    168.7 MiB
   funkwhale_postgres_1        22.73 MiB
   funkwhale_redis_1           1.496 MiB

Some users have reported running Funkwhale on Raspberry Pis with a memory
consumption of less than 350MiB.

Thus, Funkwhale should run fine on commodity hardware, small hosting boxes and
Raspberry Pi. We lack real-world examples of such deployments, so don't hesitate
do give us your feedback (either positive or negative).

Check out :doc:`optimization` for advice on how to tune your instance on small
configurations.

Software requirements
---------------------

Software requirements will vary depending of your installation method. For
Docker-based installations, the only requirement will be an Nginx reverse-proxy
that will expose your instance to the outside world.

If you plan to install your Funkwhale instance without Docker, most of the
dependencies should be available in your distribution's repositories.

.. note::

   Funkwhale works only with Python >= 3.5, as we need support for async/await.
   Older versions of Python are not supported.


Available installation methods
-------------------------------

Docker is the recommended and easiest way to setup your Funkwhale instance.
We also maintain an installation guide for Debian 9 and Arch Linux.

.. toctree::
   :maxdepth: 1

   external_dependencies
   debian
   docker
   systemd
   non_amd64_architectures

Funkwhale packages are available for the following platforms:

- `YunoHost 3 <https://yunohost.org/>`_: https://github.com/YunoHost-Apps/funkwhale_ynh (kindly maintained by `@Jibec <https://github.com/Jibec>`_)
- ArchLinux (as an AUR package): if you'd rather use a package, check out this alternative installation method on ArchLinux: https://wiki.archlinux.org/index.php/Funkwhale (package and wiki kindly maintained by getzee)
- `NixOS <https://github.com/mmai/funkwhale-nixos>`_ (kindly maintained by @mmai)

Running Funkwhale on the develop branch
---------------------------------------

Traditional deployments are done using tagged releases. However, you
may want to benefits from the latest change available, or the help detect
bugs before they are included in actual releases.

To do that, you'll need to run your instance on the develop branch,
which contains all the unreleased changes and features of the next version.

Please take into account that the develop branch
may be unstable and will contain bugs that may affect the well being of your
instance. If you are comfortable with that, you need to backup at least your database
before pulling latest changes from the develop branch.

Otherwise, the deployment process is similar to deploying with releases.
You simply need to use ``export FUNKWHALE_VERSION=develop``
in the installation and upgrade process instead of a real version number,
as we build artifacts on the development branch the same way we do for releases.

It's also recommended to check out the `develop release notes <https://dev.funkwhale.audio/funkwhale/funkwhale/blob/develop/changes/notes.rst>_` before upgrading,
since you may have to apply manual actions for your instance to continue to work. Such actions are labelled with ``[manual action required]`` in the releases notes.

.. _frontend-setup:

Frontend setup
---------------

.. note::

    You do not need to do this if you are deploying using Docker, as frontend files
    are already included in the docker image.


Files for the web frontend are purely static and can simply be downloaded, unzipped and served from any webserver:

.. parsed-literal::

    cd /srv/funkwhale
    curl -L -o front.zip "https://dev.funkwhale.audio/funkwhale/funkwhale/builds/artifacts/|version|/download?job=build_front"
    unzip front.zip

.. _reverse-proxy-setup:

Reverse proxy
--------------

In order to make Funkwhale accessible from outside your server and to play nicely with other applications on your machine, you should configure a reverse proxy.

Nginx
^^^^^

Ensure you have a recent version of nginx on your server. On Debian-like system, you would have to run the following:

.. code-block:: bash

    sudo apt-get update
    sudo apt-get install nginx

On Arch Linux and its derivatives:

.. code-block:: bash

    sudo pacman -S nginx

To avoid configuration errors at this level, we will generate an nginx configuration
using your .env file. This will ensure your reverse-proxy configuration always
match the application configuration and make upgrade/maintenance easier.

On docker deployments, run the following commands:

.. parsed-literal::

    export FUNKWHALE_VERSION="|version|"
    # download the needed files
    curl -L -o /etc/nginx/funkwhale_proxy.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/funkwhale_proxy.conf"
    curl -L -o /etc/nginx/sites-available/funkwhale.template "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/docker.proxy.template"

.. code-block:: shell

    # create a final nginx configuration using the template based on your environment
    set -a && source /srv/funkwhale/.env && set +a
    envsubst "`env | awk -F = '{printf \" $%s\", $$1}'`" \
        < /etc/nginx/sites-available/funkwhale.template \
        > /etc/nginx/sites-available/funkwhale.conf

    ln -s /etc/nginx/sites-available/funkwhale.conf /etc/nginx/sites-enabled/

On non-docker deployments, run the following commands:


.. parsed-literal::

    export FUNKWHALE_VERSION="|version|"

    # download the needed files
    curl -L -o /etc/nginx/funkwhale_proxy.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/funkwhale_proxy.conf"
    curl -L -o /etc/nginx/sites-available/funkwhale.template "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/nginx.template"

.. code-block:: shell

    # create a final nginx configuration using the template based on your environment
    set -a && source /srv/funkwhale/config/.env && set +a
    envsubst "`env | awk -F = '{printf \" $%s\", $$1}'`" \
        < /etc/nginx/sites-available/funkwhale.template \
        > /etc/nginx/sites-available/funkwhale.conf

    ln -s /etc/nginx/sites-available/funkwhale.conf /etc/nginx/sites-enabled/

.. note::

    The resulting file should not contain any variable such as ``${FUNKWHALE_HOSTNAME}``.
    You can check that using this command::

        grep '${' /etc/nginx/sites-available/funkwhale.conf

.. note::

    You can freely adapt the resulting file to your own needs, as we cannot
    cover every use case with a single template, especially when it's related
    to SSL configuration.

Finally, enable the resulting configuration:

.. code-block:: bash
    ln -s /etc/nginx/sites-available/funkwhale.conf /etc/nginx/sites-enabled/

.. note::

    At this point you will need a certificate to enable HTTPS on your server.
    There are many ways to obtain this certificate. The most popular and free
    way is to obtain it from Let's Encryt. To do this, you can use an utility
    called certbot. You can find a complete documentation on how to use certbot
    at the `certbot documentation <https://certbot.eff.org/docs/>`.

Check the configuration is valid with ``nginx -t`` then reload your nginx server with ``systemctl restart nginx``.

.. warning::

    If you plan to use to in-place import, ensure the alias value
    in the ``_protected/music`` location matches your MUSIC_DIRECTORY_SERVE_PATH
    env var.


Apache2
^^^^^^^

.. note::

    These instructions are for Debian only.
    For Arch Linux please refer to the `Arch Linux wiki <https://wiki.archlinux.org/index.php/Apache>`_.

Ensure you have a recent version of Apache2 installed on your server.
You'll also need the following dependencies::

   sudo apt-get install libapache2-mod-xsendfile

Then, download our sample virtualhost file:

.. parsed-literal::

    curl -L -o /etc/apache2/sites-available/funkwhale.conf "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/|version|/deploy/apache.conf"
    ln -s /etc/apache2/sites-available/funkwhale.conf /etc/apache2/sites-enabled/

You can tweak the configuration file according to your setup, especially the
TLS configuration. Otherwise, defaults, should work if you followed the
installation guide.

.. note::

    To obtain a certificate to enable HTTPS on your server, please refer to the note in
    the nginx chapter above.

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
