Migrating to a New Server
=========================

Sometimes, it may be necessary or desirable to migrate your
existing Funkwhale setup to a new server. This can be helpful
if you need to boost resources or if you wish to use a different
hosting platform.

Requirements
------------

To get started with your new setup, you will need to have the
following:

- `rsync <https://linux.die.net/man/1/rsync>`_ installed on the **destination** server
- SSH access set up between the two servers

Non-Docker
----------

- On the target server, run through the :doc:`installation steps<../installation/debian>` but skip the Database setup steps
- Stop all funkwhale related services on the destination server
- On the original server, create a database backup

.. code-block:: shell

    sudo -u funkwhale pg_dump -d funkwhale > "db.dump"

- On the destination server, use rsync to copy the contents of `/srv/funwkhale/data/media/music` and `/srv/funkwhale/data/music` from the original server

.. code-block:: shell

    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/data/media/ /srv/funkwhale/data/media/
    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/data/music/ /srv/funkwhale/data/music/

- Copy your .env file and database backup from your original server

.. code-block:: shell

    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/config/.env /srv/funkwhale/config/
    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/db.dump /srv/funkwhale/

- Restore the database dump

.. code-block:: shell

    sudo -u funkwhale pg_restore -d funkwhale db.dump

- Once the database has been restored, follow the database migration steps from the guide to complete the installation
- Ensure that all DNS changes have been made and start the services

Docker
------

- On the target server, run through the :doc:`installation steps<../installation/docker>` but skip the `docker-compose run --rm api python manage.py migrate` step
- Stop all funkwhale related containers on the destination server
- On the original server, create a database backup

.. code-block:: shell

    docker exec -t funkwhale_postgres_1 pg_dumpall -c -U postgres > "db.dump"

- On the destination server, use rsync to copy the contents of `/srv/funwkhale/data/media/music` and `/srv/funkwhale/data/music` from the original server

.. code-block:: shell

    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/data/media/ /srv/funkwhale/data/media/
    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/data/music/ /srv/funkwhale/data/music/

- Copy your .env file and database backup from your original server

.. code-block:: shell

    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/.env /srv/funkwhale/
    rsync -a <your username>@<original server IP/hostname>:/srv/funkwhale/db.dump /srv/funkwhale/

- Restore the database dump

.. code-block:: shell

    docker exec -i funkwhale_postgres_1 pg_restore -c -U postgres -d postgres < "db.dump"

- Once the database has been restored, run the migrations
- Ensure that all DNS changes have been made and start the services