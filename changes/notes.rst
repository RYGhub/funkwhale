Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

Denormalized audio permission logic in a separate table to enhance performance
------------------------------------------------------------------------------

With this release, we're introducing a performance enhancement that should drastically reduce the load on the database and API
servers (cf https://dev.funkwhale.audio/funkwhale/funkwhale/merge_requests/939).

Under the hood, we now maintain a separate table to link users to the tracks they are allowed to see. This change is **disabled**
by default, but will be enabled by default starting in Funkwhale 0.21.

If you want to try it now, add
``MUSIC_USE_DENORMALIZATION=True`` to your ``.env`` file, restart Funkwhale, and run the following command::

    python manage.py rebuild_music_permissions

This shouldn't cause any regression, but we'd appreciate if you could test this before the 0.21 release and report any unusual
behaviour regarding tracks, albums and artists visibility.
