Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

More reliable CLI importer
--------------------------

Our CLI importer is now more reliable and less prone to Out-of-Memory issues, especially when scanning large libraries. (hundreds of GB or bigger)

We've also improved the directory crawling logic, so that you don't have to use glob patterns or specify extensions when importing.

This means you can replace scripts that look like this::

    python api/manage.py import_files $LIBRARY_ID "/srv/funkwhale/data/music/**/*.ogg" "/srv/funkwhale/data/music/**/*.mp3" --recursive --noinput

By this:

    python api/manage.py import_files $LIBRARY_ID "/srv/funkwhale/data/music/" --recursive --noinput

And Funkwhale will happily import any supported audio file from the specified directory.
