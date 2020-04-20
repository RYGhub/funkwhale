Features
========

Scope
-----

Funkwhale is a web based audio server. It is similar in terms of goals and feature set to various existing projects, 
such as `Sonerezh <https://www.sonerezh.bzh/>`_ or `Airsonic <https://airsonic.github.io/>`_.

A social platform
------------------

However, Funkwhale is better-suited for small to medium communities and was designed to be not only a music server and player, 
but also a place to socialize around music and podcasts and discover new content. While some of these features are not currently implemented,
our roadmap includes:

- Broadcasts, as they existed in, for example, Grooveshark
- Recommendations

Content acquisition
-------------------

Audio content is uploaded to Funkwhale by users to :doc:`libraries <users/managing>` or :doc:`channels <users/channels>`, 
and admins, using a :ref:`server-side import from a directory <in-place-import>`. Content is also made available to
a pod by users following :doc:`libraries <users/follow>` and :doc:`channels <users/followchannel>`.

Metadata
--------

In order to keep your library clean, browse-able, and well-stocked with relevant data about artists, albums and tracks, we fetch a 
lot of metadata from the `MusicBrainz project <http://musicbrainz.org/>`_. Music uploaded directly to Funkwhale can also be :doc:`tagged
and edited <users/editing>` in the app itself.

Structure
---------

The project itself is split in two parts:

1. The backend, a REST API developed using Python3 and Django
2. The frontend, that consumes the API, built as a single page application with VueJS and Fomantic UI

While the main interface to the server and API is the bundled front-end, the project itself is agnostic in the way you connect to it. 
Therefore, desktop clients or apps could be developed and could implement the same (or even more) features as the bundled frontend.

This modularity also makes it possible to deploy only a single component from the system.

Federation
----------

Funkwhale makes use of the `ActivityPub protocol <https://www.w3.org/TR/activitypub/>`_ to share activities
across the `fediverse <https://en.wikipedia.org/wiki/Fediverse>`_. In particular, content uploaded in :doc:`channels <users/channels>` 
is shared publicly with other Funkwhale users as well as other ActivityPub enabled applications such as Reel2Bits 
and Mastodon, and can be followed using each application's interface. Content shared in users' libraries can be 
followed by users of other pods.
