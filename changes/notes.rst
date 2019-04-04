Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

Artist hiding in the interface
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It's now possible for users to hide artists they don't want to see.

Content linked to hidden artists will not show up in the interface anymore. Especially:

- Hidden artists tracks are removed from the current queue
- Starting a playlist will skip tracks from hidden artists
- Recently favorited, recently listened and recently added widgets on the homepage won't include content from hidden artists
- Radio suggestions will exclude tracks from hidden artists
- Hidden artists won't appear in Subsonic apps

Results linked to hidden artists will continue to show up in search results and their profile page remains accessible.

OAuth2 authorization for better integration with third-party apps
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Funkwhale now support the OAuth2 authorization and authentication protocol which will allow
third-party apps to interact with Funkwhale on behalf of users.

This feature makes it possible to build third-party apps that have the same capabilities
as Funkwhale's Web UI. The only exception at the moment is for actions that requires
special permissions, such as modifying instance settings or moderation (but this will be
enabled in a future release).

If you want to start building an app on top of Funkwhale's API, please check-out
`https://docs.funkwhale.audio/api.html`_ and `https://docs.funkwhale.audio/developers/authentication.html`_.

Better error handling and display during import
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Funkwhale should now be more resilient to missing tags in imported files, and give
you more insights when something goes wrong, including the specific tags that were missing
or invalid, and additional debug information to share in your support requests.

This information is available in all pages that list uploads, when clicking on the button next to the upload status.

Prune library command
^^^^^^^^^^^^^^^^^^^^^

Users are often surprised by Funkwhale's tendency to keep track, album and artist
metadata even if no associated files exist.

To help with that, we now offer a ``prune_library`` management command you can run
to purge your database from obsolete entry. `Please refer to our documentation
for usage instructions <https://docs.funkwhale.audio/admin/commands.html#pruning-library>`_.
