Importing music
================

From music directory on the server
----------------------------------

You can import music files in funkwhale assuming they are located on the server
and readable by the funkwhale application. Your music files should contain at
least an ``artist``, ``album`` and ``title`` tags, but we recommend you tag
it extensively using a proper tool, such as Beets or Musicbrainz Picard.

You can import those tracks as follows, assuming they are located in
``/srv/funkwhale/data/music``:

.. code-block:: bash

    python api/manage.py import_files "/srv/funkwhale/data/music/**/*.ogg" --recursive --noinput

When you use docker, the ``/srv/funkwhale/data/music`` is mounted from the host
to the ``/music`` directory on the container:

.. code-block:: bash

    docker-compose run --rm api python manage.py import_files "/music/**/*.ogg" --recursive --noinput

The import command supports several options, and you can check the help to
get details::

    docker-compose run --rm api python manage.py import_files --help

.. note::

    For the best results, we recommand tagging your music collection through
    `Picard <http://picard.musicbrainz.org/>`_ in order to have the best quality metadata.

.. note::

    This command is idempotent, meaning you can run it multiple times on the same
    files and already imported files will simply be skipped.

.. note::

    At the moment, only Flac, OGG/Vorbis and MP3 files with ID3 tags are supported


.. _in-place-import:

In-place import
^^^^^^^^^^^^^^^

By default, the CLI-importer will copy imported files to Funkwhale's internal
storage. This means importing a 1Gb library will result in the same amount
of space being used by Funkwhale.

While this behaviour has some benefits (easier backups and configuration),
it's not always the best choice, especially if you have a huge library
to import and don't want to double your disk usage.

The CLI importer supports an additional ``--in-place`` option that triggers the
following behaviour during import:

1. Imported files are not store in funkwhale anymore
2. Instead, Funkwhale will store the file path and use it to serve the music

Because those files are not managed by Funkwhale, we offer additional
configuration options to ensure the webserver can serve them properly:

- :ref:`setting-MUSIC_DIRECTORY_PATH`
- :ref:`setting-MUSIC_DIRECTORY_SERVE_PATH`

.. warning::

    While in-place import is faster and less disk-space-hungry, it's also
    more fragile: if, for some reason, you move or rename the source files,
    Funkwhale will not be able to serve those files anymore.

    Thus, be especially careful when you manipulate the source files.

Album covers
^^^^^^^^^^^^

Whenever possible, Funkwhale will import album cover, with the following precedence:

1. It will use the cover embedded in the audio files themeselves, if any (Flac/MP3 only)
2. It will use a cover.jpg or a cover.png file from the imported track directory, if any
3. It will fectch cover art from musicbrainz, assuming the file is tagged correctly

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

From other instances
--------------------

Funkwhale also supports importing music from other instances. Please refer
to :doc:`federation` for more details.
