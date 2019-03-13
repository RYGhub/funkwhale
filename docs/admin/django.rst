Using the Django Administration Backend
=======================================

Funkwhale is being actively developed, and new features are being added to the frontend all the time. However, there are some administrative tasks that can only be undertaken in the Django Administration backend.

.. Warning::
    Deleting items on the backend is **not** recommended. Deletions performed on the backend are permanent. If you remove something in the backend, you will need to re-add it from scratch.

Accessing the Django Backend
----------------------------

To access your instance's backend, navigate to ``https://yourdomain/api/admin``. You will be prompted to log in. By default, the login details will be those of the priviliged user created during the setup process.

Deleting Items
-------------------

By default, deleting items in the front end removes the file from the server but **does not** delete associated entities such as artists, albums, and track data, meaning that they will still be viewable but no longer playable. Items deleted in this way will also still count on the instance statistics. To remove them completely, it is necessary to remove them from the database entirely using the Django Administration backend.

.. Warning::
    Deleting tracks, albums, or artists will also remove them completely from any associated playlists, radios, or favorites lists. Before continuing, make sure other users on the instance are aware of the deletion(s).

Deleting a Track
^^^^^^^^^^^^^^^^

* Navigate to ``https://yourdomain/api/admin/music/track``
* Select the track(s) you wish to delete
* In the ``Action`` dropdown menu, select "Delete Selected Items"
* Click on "Go". You will be prompted to confirm the track's deletion

Deleting an Album
^^^^^^^^^^^^^^^^^

* Navigate to ``https://yourdomain/api/admin/music/album``
* Select the album(s) you wish to delete
* In the ``Action`` dropdown menu, select "Delete Selected Items"
* Click on "Go". You will be prompted to confirm the album's deletion

.. note::

    Deleting an album will remove all tracks associated with the album

Deleting an Artist
^^^^^^^^^^^^^^^^^^

* Navigate to ``https://yourdomain/api/admin/music/artist``
* Select the artist(s) you wish to delete
* In the ``Action`` dropdown menu, select "Delete Selected Items"
* Click on "Go". You will be prompted to confirm the artist's deletion

.. note::

    Deleting an artist will remove all tracks and albums associated with the artist

Removing a Followed Library
---------------------------

In Funkwhale, unfollowing a library will leave the items in place but inaccessible. To completely remove them:

* Navigate to ``https://yourdomain/api/admin/music/library/``
* Tick the box next to the library you wish to remove
* In the ``Action`` dropdown menu, select "Delete Selected Items"
* Click on "Go". You will be prompted to confirm the library's deletion

Adding Missing Album Art
-------------------------

Sometimes album art can fail to appear despite music being properly tagged. When this happens, it is possible to replace the missing art.

* Navigate to ``https://yourdomain/api/admin/music/album``
* Search for and select the album in question
* Find the item marked "Cover"
* Click "Browse" and select the file from your computer
* Click "Save" to confirm the changes

The album art will now be present on the frontend.

.. note::

    You can also clear currently loaded album art by checking the checkbox next to the current item and selecting "Clear"
