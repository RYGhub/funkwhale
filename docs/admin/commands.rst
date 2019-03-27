Management commands
===================

Pruning library
---------------

Because Funkwhale is a multi-user and federated audio server, we don't delete any artist, album
and track objects in the database when you delete the corresponding files.

This is on purpose, because those objects may be referenced in user playlists, favorites,
listening history or on other instances, or other users could have upload files matching
linked to those entities in their own private libraries.

Therefore, Funkwhale has a really conservative approach and doesn't delete metadata when
audio files are deleted.

This behaviour can be problematic in some situations though, e.g. if you imported
a lot of wrongly tagged files, then deleted the files to reimport them later.

To help with that, we provide a management you can run on the server and that will effectively
prune you library from track, album and artist metadata that is not tied to any file:

.. code-block:: sh

    # print help
    python manage.py prune_library --help

    # prune tracks with no uploads
    python manage.py prune_library --tracks

    # prune albums with no tracks
    python manage.py prune_library --albums

    # prune artists with no tracks/albums
    python manage.py prune_library --artists

    # prune everything (tracks, albums and artists)
    python manage.py prune_library --tracks --albums --artists

The ``prune_library`` command will not delete anything by default, and only gives
you an estimate of how many database objects would be affected by the pruning.

Once you have reviewed the output and are comfortable with the changes, you should rerun
the command with the ``--no-dry-run`` flag to disable dry run mode and actually apply
the changes on the database.

.. warning::

    Running this command with ``--no-dry-run`` is irreversible. Unless you have a backup,
    there will be no way to retrieve the deleted data.

.. note::

    The command will exclude tracks that are favorited, included in playlists or listening
    history by default. If you want to include those in the pruning process as well,
    add the corresponding ``--ignore-favorites``, ``--ignore-playlists`` and ``--ignore-listenings``
    flags.
