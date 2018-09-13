Features
=========

Scope
------

Funkwhale is a web based music server. It is similar in term of goals and feature set to various existing projects, such as `Sonerezh <https://www.sonerezh.bzh/>`_ or `Airsonic <https://airsonic.github.io/>`_.

A social platform
------------------

However, Funkwhale is better-suited for small to medium communities and was designed to be not only a music server and player, but also a place to socialize around music and discover new content. While some of these features are not currently implemented, our roadmap includes:

- Radios, to discover the music of a given user, artist, genre...
- Playlists
- Favorites
- Broadcasts, as they existed in Grooveshark, for example
- Recommendations

Music acquisition
------------------

Funkwhale is not bundled with any music, and you'll have to import your own music in the platform using the bundled plugins.

At the moment, you can feed your existing music library to the server and, assuming it has the correct tags defined on the files, it will be imported seamlessly.

You can also import music directly from YouTube (other sources coming, thanks to `Youtube-dl <https://github.com/rg3/youtube-dl>`_). Downloading and publishing copyrighted content may be forbidden in your country, though.

Metadata
---------

In order to keep your library clean, browsable and aggregate relevant data about artists, albums and tracks, we fetch a lot of metadata from the `MusicBrainz project <http://musicbrainz.org/>`_.

Structure
---------

The project itself is splitted in two parts:

1. The backend, a REST API developped using Python3 and Django
2. The frontend, that consumes the API, built as a single page application with VueJS and Semantic UI

While the main interface to the server and API is the bundled front-end, the project itself is agnostic in the way you connect to it. Therefore, desktop clients or apps could be developped and implement the same (or even more) features as the bundled frontend.

This modularity also makes it possible do deploy only a single component from the system.

Federation
----------

Each Funkwhale instance is able to fetch music from other compatible servers,
and share its own library on the network. The federation is implemented
using the ActivityPub protocol, in order to leverage existing tools
and be compatible with other services such as Mastodon.

As of today, federation only targets music acquisition, meaning user interaction
are not shared via ActivityPub. This will be implemented at a later point.
