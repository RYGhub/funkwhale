External dependencies
=====================


.. note::

    Those dependencies are handled automatically if you are
    :doc:`deploying using docker <./docker>`

Database setup (PostgreSQL)
---------------------------

Funkwhale requires a PostgreSQL database to work properly. Please refer
to the `PostgreSQL documentation <https://www.postgresql.org/download/>`_
for installation instructions specific to your os.

On Debian-like systems, you would install the database server like this:

.. code-block:: shell

    sudo apt-get install postgresql postgresql-contrib

On Arch Linux and its derivatives:

.. code-block:: shell

    sudo pacman -S postgresql

On Arch, you'll also need to initialize the database. See `the Arch Linux wiki <https://wiki.archlinux.org/index.php/Postgresql#Initial_configuration>`_.

The remaining steps are heavily inspired from `this Digital Ocean guide <https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04>`_.

Open a database shell:

.. code-block:: shell

    sudo -u postgres psql

Create the project database and user:

.. code-block:: shell

    CREATE DATABASE "funkwhale"
      WITH ENCODING 'utf8';
    CREATE USER funkwhale;
    GRANT ALL PRIVILEGES ON DATABASE funkwhale TO funkwhale;

.. warning::

    It's important that you use utf-8 encoding for your database,
    otherwise you'll end up with errors and crashes later on when dealing
    with music metedata that contains non-ascii chars.


On Debian you will also need to allow the funkwhale unix user to access the database:

.. code-block:: shell

    cat | sudo tee -a /etc/postgresql/9.5/main/pg_hba.conf << EOF
    local   all             funkwhale                               peer
    EOF
    sudo systemctl restart postgresql

Assuming you already have :ref:`created your funkwhale user <create-funkwhale-user>`,
you should now be able to open a postgresql shell:

.. code-block:: shell

    sudo -u funkwhale -H psql

Unless you give a superuser access to the database user, you should also
enable some extensions on your database server, as those are required
for Funkwhale to work properly:

.. code-block:: shell

    sudo -u postgres psql funkwhale -c 'CREATE EXTENSION "unaccent";'


Cache setup (Redis)
-------------------

Funkwhale also requires a cache server:

- To make the whole system faster, by caching network requests or database
  queries
- To handle asynchronous tasks such as music import

On Debian-like distributions, a redis package is available, and you can
install it:

.. code-block:: shell

    sudo apt-get install redis-server

On Arch Linux and its derivatives:

.. code-block:: shell

    sudo pacman -S redis

This should be enough to have your redis server set up.
