Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

Edits on tracks, albums and artists
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Funkwhale was a bit annoying when it camed to metadata. Tracks, albums and artists profiles
were created from audio file tags, but basically immutable after that (unless you had
admin access to Django's UI, which wasn't ideal to do this kind of changes).

With this release, everyone can suggest changes on track, album and artist pages. Users
with the "library" permission can review suggested edits in a dedicated interface
and apply/reject them.

Approved edits are broadcasted via federation, to ensure other instances get the information
too.

Not all fields are currently modifiable using this feature. Especially, it's not possible
to suggest a new album cover, or reassign a track to a different album or artist. Those will
be implemented in a future release.

Admin UI for tracks, albums, artists, libraries and uploads
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As part of our ongoing effort to make Funkwhale easier to manage for instance owners,
this release includes a brand new administration interface to deal with:

- tracks
- albums
- artists
- libraries
- uploads

You can use this UI to quickly search for any object, delete objects in batch, understand
where they are coming from etc. This new UI should remove the need to go through Django's
admin in the vast majority of cases (but also includes a link to Django's admin when needed).


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

Support for S3-compatible storages to store media files
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Storing all media files on the Funkwhale server itself may not be possible or desirable
in all scenarios. You can now configure Funkwhale to store those files in a S3
bucket instead.

Check-out `https://docs.funkwhale.audio/admin/external-storages.html`_ if you want to use
this feature.

Prune library command
^^^^^^^^^^^^^^^^^^^^^

Users are often surprised by Funkwhale's tendency to keep track, album and artist
metadata even if no associated files exist.

To help with that, we now offer a ``prune_library`` management command you can run
to purge your database from obsolete entries. `Please refer to our documentation
for usage instructions <https://docs.funkwhale.audio/admin/commands.html#pruning-library>`_.

Check in-place files command
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When using in-place import with a living audio library, you'll quite often rename or
remove files from the file system. Unfortunately, Funkwhale keeps a reference to those
files in the database, which results in unplayable tracks.

To help with that, we now offer a ``check_inplace_files`` management command you can run
to purge your database from obsolete files. `Please refer to our documentation
for usage instructions <https://docs.funkwhale.audio/admin/commands.html#remove-obsolete-files-from-database>`_.
