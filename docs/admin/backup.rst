Backup your Funkwhale instance
==============================

.. note::

    Before upgrading your instance, we strongly advise you to make at least a database backup. Ideally, you should make a full backup, including the database and the media files.


Docker setup
------------

If you've followed the setup instructions in :doc:`../installation/docker`, here is the backup path:

Multi-container installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Backup the db
^^^^^^^^^^^^^

On docker setups, you have to ``pg_dumpall`` in container ``funkwhale_postgres_1``:

.. code-block:: shell

   docker exec -t funkwhale_postgres_1 pg_dumpall -c -U postgres > dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql

Backup the media files
^^^^^^^^^^^^^^^^^^^^^^

To backup docker data volumes, as the volumes are bound mounted to the host, the ``rsync`` way would go like this:

.. code-block:: shell

    rsync -avzhP /srv/funkwhale/data/media /path/to/your/backup/media
    rsync -avzhP /srv/funkwhale/data/music /path/to/your/backup/music


Backup the configuration files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On docker setups, the configuration file is located at the root level:

.. code-block:: shell

    rsync -avzhP /srv/funkwhale/.env /path/to/your/backup/.env


Non-docker setup
----------------

Backup the db
^^^^^^^^^^^^^

On non-docker setups, you have to ``pg_dump`` as user ``postgres``:

.. code-block:: shell

   sudo -u postgres -H pg_dump funkwhale > /path/to/your/backup/dump_`date +%d-%m-%Y"_"%H_%M_%S`.sql

Backup the media files
^^^^^^^^^^^^^^^^^^^^^^

A simple way to backup your media files is to use ``rsync``:

.. code-block:: shell

    rsync -avzhP /srv/funkwhale/data/media /path/to/your/backup/media
    rsync -avzhP /srv/funkwhale/data/music /path/to/your/backup/music

Backup the configuration files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: shell

    rsync -avzhP /srv/funkwhale/config/.env /path/to/your/backup/.env

.. note::
   You may also want to backup your proxy configuration file.

   For frequent backups, you may want to use deduplication and compression to keep the backup size low. In this case, a tool like ``borg`` will be more appropriate.
