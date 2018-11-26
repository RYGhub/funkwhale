Subsonic API
============

Funkwhale implements a subset of the `Subsonic API <http://www.subsonic.org/pages/api.jsp>`_ that makes it compatible
with various apps in the Subsonic ecosystem (See :doc:`../users/apps`).

Supported endpoints
-------------------

We seek the best compatibility with existing apps and wil eventually implement
all endpoints that match Funkwhale's feature set. However, the current implementation
do not include folder-based endpoints, as it does not match our internal model at all
and will require substantial effort to emulate.

We'll try to keep this list up-to-date, but you can also browse `the relevant code
<https://code.eliotberriot.com/funkwhale/funkwhale/blob/develop/api/funkwhale_api/subsonic/views.py>`_
if needed.

As of today, the following endpoints are implemented:

- createPlaylist
- deletePlaylist
- getAlbum
- getAlbumList2
- getArtist
- getArtistInfo2
- getArtists
- getAvatar
- getCoverArt
- getIndexes
- getLicense
- getMusicFolders
- getPlaylist
- getPlaylists
- getRandomSongs
- getSong
- getStarred
- getStarred2
- getUser
- ping
- scrobble
- search3
- star
- stream
- unstar
- updatePlaylist

We support both XML and JSON formats for all those endpoints.

Additional properties
---------------------

Regardless of the endpoints, we always return those additional properties
in our payload, which you can use to adapt your client behaviour if needed:

.. code-block:: json

    {
        "subsonic-response": {
            ...
            "type": "funkwhale",
            "funkwhaleVersion": "0.17"
        }
    }

Testing a Subsonic app
----------------------

We maintain a demo server at https://demo.funkwhale.audio/, which you can use for
your tests. Example with the ping endpoint: https://demo.funkwhale.audio/rest/ping.view?f=json
