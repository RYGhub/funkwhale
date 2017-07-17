Importing music
================

From music directory on the server
----------------------------------

You can import music files in funkwhale assuming they are located on the server
and readable by the funkwhale application. Your music files should contain at
least an ``artist``, ``album`` and ``title`` tags.

You can import those tracks as follows, assuming they are located in
``/srv/funkwhale/data/music``:

.. code-block:: bash

    python api/manage.py import_files "/srv/funkwhale/data/music/**/*.ogg" --recursive --noinput

When you use docker, the ``/srv/funkwhale/data/music`` is mounted from the host
to the ``/music`` directory on the container:

.. code-block:: bash

    docker-compose run --rm api python manage.py import_files "/music/**/*.ogg" --recursive --noinput

For the best results, we recommand tagging your music collection through
`Picard <http://picard.musicbrainz.org/>`_ in order to have the best quality metadata.


.. note::

    This command is idempotent, meaning you can run it multiple times on the same
    files and already imported files will simply be skipped.

.. note::

    At the moment, only OGG/Vorbis and MP3 files with ID3 tags are supported

.. note::

    The --recursive flag will work only on Python 3.5+, which is the default
    version When using Docker or Debian 9. If you use an older version of Python,
    remove the --recursive flag and use more explicit import patterns instead::

        # this will only import ogg files at the second level
        "/srv/funkwhale/data/music/*/*.ogg"
        # this will only import ogg files in the fiven directory
        "/srv/funkwhale/data/music/System-of-a-down/*.ogg"



Getting demo tracks
^^^^^^^^^^^^^^^^^^^

If you do not have any music on your server but still want to test the import
process, you can call the following methods do download a few albums licenced
under creative commons (courtesy of Jamendo):

.. parsed-literal::

    curl -L -o download-tracks.sh "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/demo/download-tracks.sh"
    curl -L -o music.txt "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/demo/music.txt"
    chmod +x download-tracks.sh
    ./download-tracks.sh music.txt

This will download a bunch of zip archives (one per album) under the ``data/music`` directory and unzip their content.
