Tagging Music With MusicBrainz Picard
=====================================

In order to get the most out of Funkwhale, it is important to tag files correctly. Good tagging makes managing your library much easier and provides Funkwhale with the information necessary to display album art, metadata, and other useful information. The recommended tool for tagging music is `MusicBrainz Picard <https://picard.musicbrainz.org/>`_.

Tagging Items
--------------

Tagging a File
^^^^^^^^^^^^^^

To load a file into MusicBrainz Picard:

* Click on "Add Files"
* Select the files you want to tag from your computer
* Picard should automatically start scanning the items. If nothing happenes, select the item(s) and click on "Scan"
* Picard will start assigning suitable tags
* Hit ctrl+s or click "Save" to save the tags to the file

Tagging a Directory
^^^^^^^^^^^^^^^^^^^

* Click on "Add Folder"
* Select the directory of files you want to tag from your computer
* Picard should automatically start scanning the items. If nothing happenes, select the item(s) and click on "Scan"
* Picard will start assigning suitable tags
* Hit ctrl+s or click "Save" to save the tags to the file


Alternative Versions
--------------------

Picard is generally accurate when it comes to determining the release of an album/track, but sometimes it can fail to get the right version. You can force it to use a particular version of an album or track using the following method:

Alternative Albums
^^^^^^^^^^^^^^^^^^

* Load the directory into Picard
* Once it has tagged the full album, right-click on the album and hover over "other versions"
* Select the collect release from the list
* Do this for any duplicate items until all tracks are under the correct release
* Hit ctrl+s or click "Save" to save the tags to the files

Alternative Tracks
^^^^^^^^^^^^^^^^^^

If a track is not picking up its release, do the following:

* Right-click on the offending track and select "Search for Similar Tracks..."
* Search for your release using `MusicBrainz's search syntax <https://musicbrainz.org/doc/Indexed_Search_Syntax>`_
* Select the correct track from the list and click on "Load into Picard"
* The track will now inherit tags from the selected track. Hit ctrl+s or click "Save" to save the tags to the file

Adding Items to MusicBrainz
---------------------------

MusicBrainz is an ever-growing library of music, but it may not yet have an entry for certain items. You can add these yourself by following their `guide <https://musicbrainz.org/doc/How_to_Add_a_Release/>`_.

Once you've added a new item, Picard should automatically pick up the new details based on the files' metadata. This means that it will tag the music not only for you, but for any other user who tries to tag the same item in the future.