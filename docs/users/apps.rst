Using Funkwhale from other apps
===============================

As of today, the only official client for using Funkwhale is the web client,
the one you use in your browser.

While the web client works okay, it's still not ready for some use cases, especially:

- Usage on narrow/touch screens (smartphones, tablets)
- Usage on the go, with an intermittent connection

This pages lists alternative clients you can use to connect to your Funkwhale
instance and enjoy your music.


Subsonic-compatible clients
---------------------------

Since version 0.12, Funkwhale implements a subset of the `Subsonic API <http://www.subsonic.org/pages/api.jsp>`_.
This API is a de-facto standard for a lot of projects out there, and many clients
are available that works with this API.

Those Subsonic features are supported in Funkwhale:

- Search (artists, albums, tracks)
- Common library browsing using ID3 tags (list artists, albums, etc.)
- Playlist management
- Stars (which is mapped to Funkwhale's favorites)

Those features as missing:

- Transcoding/streaming with different bitrates
- Album covers
- Artist info (this data is not available in Funkwhale)
- Library browsing that relies music directories
- Bookmarks
- Admin
- Chat
- Shares

.. note::

    If you know or use some recent, well-maintained, Subsonic clients,
    please get in touch so we can add them to this list.

    Especially we're still lacking an iOS client!


Enabling Subsonic on your Funkwhale account
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To log-in on your Funkwhale account from Subsonic clients, you will need to
set a separate Subsonic API password by visiting your settings page.

Then, when using a client, you'll have to input some information about your server:

1. Your Funkwhale instance URL (e.g. https://demo.funkwhale.audio)
2. Your Funkwhale username (e.g. demo)
3. Your Subsonic API password (the one you set earlier in this section)

In your client configuration, please double check the "ID3" or "Browse with tags"
setting is enabled.

Ultrasonic (Android)
^^^^^^^^^^^^^^^^^^^^

- Price: free
- F-Droid: https://f-droid.org/en/packages/org.moire.ultrasonic/
- Google Play: https://play.google.com/store/apps/details?id=org.moire.ultrasonic
- Sources: https://github.com/ultrasonic/ultrasonic


Ultrasonic is a full-featured Subsonic client with Playlists, Stars, Search,
Offline mode, etc.

It's one of the recommended Android client to use with Funkwhale, as we are doing
our Android tests on this one.


DSub (Android)
^^^^^^^^^^^^^^

- Price: free (on F-Droid)
- F-Droid: https://f-droid.org/en/packages/github.daneren2005.dsub/
- Google Play: https://play.google.com/store/apps/details?id=github.daneren2005.dsub
- Sources: https://github.com/daneren2005/Subsonic

DSub is a full-featured Subsonic client that works great, and has a lot of features:

- Playlists
- Stars
- Search
- Offline cache (with configurable size, playlist download, queue prefetching, etc.)

It's one of the recommended Android client to use with Funkwhale, as we are doing
our Android tests on this one.

Clementine (Desktop)
^^^^^^^^^^^^^^^^^^^^

- Price: free
- Website: https://www.clementine-player.org/fr/

This desktop client works on Windows, Mac OS X and Linux and is able to stream
music from your Funkwhale instance. However, it does not implement advanced
features such as playlist management, search or stars.

This is the client we use for our desktop tests.
