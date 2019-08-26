Funkwhale CLI examples
======================

Uploading local files
---------------------

**Goal**: create a library and upload all MP3 files from ``~/Music`` to it

**Commands**::

    funkwhale libraries create --name "My awesome library" --visibility me
    # copy the returned UUID
    funkwhale uploads create <UUID> ~/Music/**/*.mp3


Favorite an entire album
------------------------

**Goal**: retrieve all the tracks from an album and add these to your favorites

**Commands**::

    # retrieve the album ID
    funkwhale albums ls "The Slip"

    # Copy the ID, then retrieve 100 pages of tracks from that album
    # get only the IDs and pipe those to the favorite creation command
    funkwhale tracks ls -f "album=<ID>" --ids --limit 100 \
        | xargs funkwhale favorites tracks create


Mirror an artist discography locally
------------------------------------

**Goal**: Download the discography of an artist locally, in the ``~/Music`` directory, in an ``Artist/Album/Track`` folder hierarchy

**Commands**::

    # retrieve the artist ID
    funkwhale artists ls "Nine Inch Nails"

    # Copy the ID, then retrieve 100 pages of tracks from that artist
    # get only the IDs and pipe those to the download command
    funkwhale tracks ls -f "artist=<ID>" --ids --limit 100 \
        | xargs funkwhale tracks download \
            -f mp3 -d ~/Music -t "{artist}/{album}/{title}.{extension}"


Open a remote album in VLC
--------------------------

**Goal**: Variation of the previous example, but instead of downloading an artist discography, we listen to an album in VLC

**Commands**::

    # retrieve the album ID
    funkwhale albums ls "The Slip"

    # Copy the ID, then retrieve 100 pages of tracks from that album
    # get only the IDs, download the corresponding tracks and pipe the audio
    # directly to VLC
    funkwhale tracks ls -f "album=<ID>" --ids --limit 100 \
        | xargs funkwhale tracks download \
        | vlc -
