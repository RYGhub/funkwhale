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

On debian-like systems, you would install the database server like this:

.. code-block:: shell

    sudo apt-get install postgresql

The remaining steps are heavily inspired from `this Digital Ocean guide <https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-16-04>`_.

Open a database shell:

.. code-block:: shell

    sudo -u postgres psql

Create the project database and user:

.. code-block:: shell

    CREATE DATABASE funkwhale;
    CREATE USER funkwhale;
    GRANT ALL PRIVILEGES ON DATABASE funkwhale TO funkwhale;

Assuming you already have :ref:`created your funkwhale user <create-funkwhale-user>`,
you should now be able to open a postgresql shell:

.. code-block:: shell

    sudo -u funkwhale -H psql

Unless you give a superuser access to the database user, you should also
enable some extensions on your database server, as those are required
for funkwhale to work properly:

.. code-block:: shell

    sudo -u postgres psql -c 'CREATE EXTENSION "unaccent";'


Cache setup (Redis)
-------------------

Funkwhale also requires a cache server:

- To make the whole system faster, by caching network requests or database
  queries
- To handle asynchronous tasks such as music import

On debian-like distributions, a redis package is available, and you can
install it:

.. code-block:: shell

    sudo apt-get install redis-server

This should be enough to have your redis server set up.
