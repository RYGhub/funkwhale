Debian and Arch Linux installation
==================================

.. note::

    This guide targets Debian 9 (Stretch), which is the latest Debian, as well as Arch Linux.

External dependencies
---------------------

The guides will focus on installing Funkwhale-specific components and
dependencies. However, Funkwhale requires a
:doc:`few external dependencies <./external_dependencies>` for which
documentation is outside of this document scope.

Install utilities
-----------------

You'll need a few utilities during this guide that are not always present by
default on system. On Debian-like systems, you can install them using:

.. code-block:: shell

    sudo apt-get update
    sudo apt-get install curl python3-pip python3-venv git unzip

On Arch Linux and its derivatives:

.. code-block:: shell

    sudo pacman -S curl python-pip python-virtualenv git unzip

Layout
-------

All Funkwhale-related files will be located under ``/srv/funkwhale`` apart
from database files and a few configuration files. We will also have a
dedicated ``funkwhale`` user to launch the processes we need and own those files.

You are free to use different values here, just remember to adapt those in the
next steps.

.. _create-funkwhale-user:

Create the user and the directory:

.. code-block:: shell

    sudo useradd -r -s /usr/bin/nologin -d /srv/funkwhale -m funkwhale
    cd /srv/funkwhale

Log in as the newly created user from now on:

.. code-block:: shell

    sudo -u funkwhale -H bash

Now let's setup our directory layout. Here is how it will look like::

    .
    ├── config      # config / environment files
    ├── api         # api code of your instance
    ├── data        # persistent data, such as music files
    ├── front       # frontend files for the web user interface
    └── virtualenv  # python dependencies for Funkwhale

Create the aforementionned directories:

.. code-block:: shell

    mkdir -p config api data/static data/media data/music front

The ``virtualenv`` directory is a bit special and will be created separately.

Download latest Funkwhale release
----------------------------------

Funkwhale is splitted in two components:

1. The API, which will handle music storage and user accounts
2. The frontend, that will simply connect to the API to interact with its data

Those components are packaged in subsequent releases, such as 0.1, 0.2, etc.
You can browse the :doc:`changelog </changelog>` for a list of available releases
and pick the one you want to install, usually the latest one should be okay.

In this guide, we'll assume you want to install the latest version of Funkwhale,
which is |version|:

First, we'll download the latest api release.

.. parsed-literal::

    curl -L -o "api-|version|.zip" "https://code.eliotberriot.com/funkwhale/funkwhale/-/jobs/artifacts/|version|/download?job=build_api"
    unzip "api-|version|.zip" -d extracted
    mv extracted/api/* api/
    rm -rf extracted


Then we'll download the frontend files:

.. parsed-literal::

    curl -L -o "front-|version|.zip" "https://code.eliotberriot.com/funkwhale/funkwhale/-/jobs/artifacts/|version|/download?job=build_front"
    unzip "front-|version|.zip" -d extracted
    mv extracted/front .
    rm -rf extracted

You can leave the ZIP archives in the directory, this will help you know
which version you've installed next time you want to upgrade your installation.

System dependencies
-------------------

First, switch to the api directory:

.. code-block:: shell

    cd api

A few OS packages are required in order to run Funkwhale. On Debian-like
 systems, the list is available in ``api/requirements.apt`` or by running
``./install_os_dependencies.sh list`` and in ``api/requirements.pac`` on
Arch.

.. note::

    Ensure you are running the next commands as root or using sudo
    (and not as the funkwhale) user.

You can install those packages all at once:

On Debian-like systems:

.. code-block:: shell

    ./install_os_dependencies.sh install

On Arch Linux and its derivatives:

.. code-block:: shell

    pacman -S $(cat api/requirements.pac)

From now on you can switch back to the funkwhale user.

Python dependencies
--------------------

Go back to the base directory:

.. code-block:: shell

    cd /srv/funkwhale

To avoid collisions with other software on your system, Python dependencies
will be installed in a dedicated
`virtualenv <https://docs.python.org/3/library/venv.html>`_.

First, create the virtualenv and install wheel:

.. code-block:: shell

    python3 -m venv /srv/funkwhale/virtualenv
    pip3 install wheel

This will result in a ``virtualenv`` directory being created in
``/srv/funkwhale/virtualenv``.

In the rest of this guide, we'll need to activate this environment to ensure
dependencies are installed within it, and not directly on your host system.

This is done with the following command:

.. code-block:: shell

    source /srv/funkwhale/virtualenv/bin/activate

Finally, install the python dependencies:

.. code-block:: shell

    pip3 install -r api/requirements.txt

.. important::

    Further commands involving python should always be run after you activated
    the virtualenv, as described earlier, otherwise those commands will raise
    errors


Environment file
----------------

You can now start to configure Funkwhale. The main way to achieve that is by
adding an environment file that will host settings that are relevant to your
installation.

Download the sample environment file:

.. parsed-literal::

    curl -L -o config/.env "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/env.prod.sample"

You can then edit it: the file is heavily commented, and the most relevant
configuration options are mentionned at the top of the file.

Especially, populate the ``DATABASE_URL`` and ``CACHE_URL`` values based on
how you configured your PostgreSQL and Redis servers in
:doc:`external dependencies <./external_dependencies>`.


When you want to run command on the API server, such as to create the
database or compile static files, you have to ensure you source
the environment variables.

This can be done like this::

    export $(cat config/.env | grep -v ^# | xargs)

The easier thing to do is to store this in a script::

    cat > /srv/funkwhale/load_env <<'EOL'
    #!/bin/bash
    export $(cat /srv/funkwhale/config/.env | grep -v ^# | xargs)
    EOL
    chmod +x /srv/funkwhale/load_env

You should now be able to run the following to populate your environment
variables easily:

.. code-block:: shell

    source /srv/funkwhale/load_env

.. note::

    Remember to source ``load_env`` whenever you edit your .env file.

Database setup
---------------

You should now be able to import the initial database structure:

.. code-block:: shell

    python3 api/manage.py migrate

This will create the required tables and rows.

.. note::

    You can safely execute this command any time you want, this will only
    run unapplied migrations.

.. warning::

    You may sometimes get the following warning while applying migrations::

        "Your models have changes that are not yet reflected in a migration, and so won't be applied."

    This is a warning, not an error, and it can be safely ignored.
    Never run the ``makemigrations`` command yourself.

Create an admin account
-----------------------

You can then create your first user account:

.. code-block:: shell

    python3 api/manage.py createsuperuser

If you ever want to change a user's password from the command line, just run:

.. code-block:: shell

    python3 api/manage.py changepassword <user>

Collect static files
--------------------

Static files are the static assets used by the API server (icon PNGs, CSS, etc.).
We need to collect them explicitly, so they can be served by the webserver:

.. code-block:: shell

    python3 api/manage.py collectstatic

This should populate the directory you choose for the ``STATIC_ROOT`` variable
in your ``.env`` file.

Systemd unit file
------------------

See :doc:`./systemd`.

Reverse proxy setup
--------------------

See :ref:`reverse-proxy <reverse-proxy-setup>`.
