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
    sudo apt-get install curl python3-pip python3-venv git unzip libldap2-dev libsasl2-dev

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

    curl -L -o "api-|version|.zip" "https://dev.funkwhale.audio/funkwhale/funkwhale/-/jobs/artifacts/|version|/download?job=build_api"
    unzip "api-|version|.zip" -d extracted
    mv extracted/api/* api/
    rm -rf extracted


Then we'll download the frontend files:

.. parsed-literal::

    curl -L -o "front-|version|.zip" "https://dev.funkwhale.audio/funkwhale/funkwhale/-/jobs/artifacts/|version|/download?job=build_front"
    unzip "front-|version|.zip" -d extracted
    mv extracted/front .
    rm -rf extracted

.. note::

    You can also choose to get the code directly from the git repo. In this
    case, run

        cd /srv

        rm -r funkwhale

        git clone -b master https://dev.funkwhale.audio/funkwhale/funkwhale funkwhale

        cd funkwhale

    The above clone command uses the master branch instead of the default develop branch, as master is stable and more suited for production setups.

    You'll also need to re-create the folders we make earlier:

        mkdir -p config data/static data/media data/music front

    You will still need to get the frontend files as specified before, because
    we're not going to build them.


You can leave the ZIP archives in the directory, this will help you know
which version you've installed next time you want to upgrade your installation.

System dependencies
-------------------

First, switch to the api directory:

.. code-block:: shell

    cd api

A few OS packages are required in order to run Funkwhale. On Debian-like
systems, they can be installed with

.. code-block:: shell

    sudo apt install build-essential ffmpeg libjpeg-dev libmagic-dev libpq-dev postgresql-client python3-dev

On Arch, run

.. code-block:: shell

    pacman -S $(cat api/requirements.pac)

From now on, you should use the funkwhale user for all commands.

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

    pip install -r api/requirements.txt

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

    curl -L -o config/.env "https://dev.funkwhale.audio/funkwhale/funkwhale/raw/develop/deploy/env.prod.sample"

.. note::

    if you used git to get the latest version of the code earlier, you can instead do

        cp /srv/funkwhale/deploy/env.prod.sample /srv/funkwhale/config/.env


You can then edit it: the file is heavily commented, and the most relevant
configuration options are mentioned at the top of the file.

Especially, populate the ``DATABASE_URL`` and ``CACHE_URL`` values based on
how you configured your PostgreSQL and Redis servers in
:doc:`external dependencies <./external_dependencies>`.

.. note::

    The environment file at config/.env is loaded automatically by Funkwhale processes.

Database setup
---------------

You should now be able to import the initial database structure:

.. code-block:: shell

    python api/manage.py migrate

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

    python api/manage.py createsuperuser

If you ever want to change a user's password from the command line, just run:

.. code-block:: shell

    python api/manage.py changepassword <user>

Collect static files
--------------------

Static files are the static assets used by the API server (icon PNGs, CSS, etc.).
We need to collect them explicitly, so they can be served by the webserver:

.. code-block:: shell

    python api/manage.py collectstatic

This should populate the directory you choose for the ``STATIC_ROOT`` variable
in your ``.env`` file.

Systemd unit file
------------------

See :doc:`./systemd`.

Reverse proxy setup
--------------------

See :ref:`reverse-proxy <reverse-proxy-setup>`.
