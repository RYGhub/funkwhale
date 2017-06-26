Importing music
================

From music directory on the server
----------------------------------

You can import music files in funkwhale assuming they are located on the server
and readable by the funkwhale application.

Assuming your music is located at ``/music`` and your music files contains at
least an ``artist``, ``album`` and ``title`` tag, you can import those tracks as follows:

.. code-block:: bash

    docker-compose run --rm api python manage.py import_files "/music/**/*.ogg" --recursive --noinput

For the best results, we recommand tagging your music collection through
`Picard <http://picard.musicbrainz.org/>`_ in order to have the best quality metadata.

.. note::

    This command is idempotent, meaning you can run it multiple times on the same
    files and already imported files will simply be skipped.

.. note::

    At the moment, only OGG/Vorbis and MP3 files with ID3 tags are supported


Getting demo tracks
^^^^^^^^^^^^^^^^^^^

If you do not have any music on your server but still want to test the import
process, you can call the following methods do download a few albums licenced
under creative commons (courtesy of Jamendo):

.. code-block:: bash

    curl -L -o download-tracks.sh "https://code.eliotberriot.com/funkwhale/funkwhale/raw/master/demo/download-tracks.sh"
    curl -L -o music.txt "https://code.eliotberriot.com/funkwhale/funkwhale/raw/master/demo/music.txt"
    chmod +x download-tracks.sh
    ./download-tracks.sh music.txt

This will download a bunch of zip archives (one per album) under the ``data/music`` directory and unzip their content.
