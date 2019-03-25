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
