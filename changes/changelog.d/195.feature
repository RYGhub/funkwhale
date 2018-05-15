Store file length, size and bitrate (#195)


Storage of bitrate, size and length in database
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Starting with this release, when importing files, Funkwhale will store
additional information about audio files:

- Bitrate
- Size (in bytes)
- Duration

This change is not retroactive, meaning already imported files will lack those
informations. The interface and API should work as before in such case, however,
we offer a command to deal with legacy files and populate the missing values.

On docker setups:

.. code-block:: shell

    docker-compose run --rm api python manage.py fix_track_files


On non-docker setups:

.. code-block:: shell

    # from your activated virtualenv
    python manage.py fix_track_files

.. note::

    The execution time for this command is proportional to the number of
    audio files stored on your instance. This is because we need to read the
    files from disk to fetch the data. You can run it in the background
    while Funkwhale is up.

    It's also safe to interrupt this command and rerun it at a later point, or run
    it multiple times.

    Use the --dry-run flag to check how many files would be impacted.
