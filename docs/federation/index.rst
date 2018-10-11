Funkwhale Federation
====================

This documentation section is more technical, and targets people who want
to understand how Funkwhale's federation works.


Technologies and standards
--------------------------

Funkwhale's federation is built on top of the following technologies:

- `ActivityPub`_ as the high-level federation protocol
- `HTTP Signatures`_ as the primary mean to authenticate messages
- `Webfinger`_ to easily retrive resources using human-friendly names
- `ActivityStreams`_ and `ActivityStreams vocabulary`_ as the mean to structure messages

Support for the following is planned but not implemented-yet:

- `JSON-LD signatures`_ as an alternate mean to authenticate messages

.. _ActivityPub: https://www.w3.org/TR/activitypub/
.. _HTTP Signatures: https://tools.ietf.org/id/draft-cavage-http-signatures-01.html
.. _Webfinger: https://tools.ietf.org/html/rfc7033
.. _JSON-LD signatures: https://w3c-dvcg.github.io/ld-signatures/
.. _ActivityStreams: https://www.w3.org/TR/activitystreams-core/
.. _ActivityStreams vocabulary: https://www.w3.org/TR/activitystreams-vocabulary/

Philosophy
----------

Our goal is to stick to the specifications as much as possible, to ensure
compatibility with existing applications such as Mastodon, Peertube, Plume, Pleroma or PixelFed.

However, this is not always possible for all our use cases. The ActivityPub and ActivityStreams specifications
are really high-level and do not always fit our use cases. For such cases, we will
use an ad-hoc solution, and document it here.

There are plenty of projects built using ActivityPub, and our goal is not to support all
the existing activities. Instead, we want to support activities and objects that make sense
for Funkwhale use cases, such as follows or likes.

If you think this document is not accurate or find evidence that Funkwhale is not
behaving according to the behaviour documented here, please file a bug on our
issue tracker, as we consider this a bug.

Internal logic
--------------

This section is relevant if you're interested in how we handle things internally
in our application code.

Database schema
^^^^^^^^^^^^^^^

As much as possible, we try to map our internal model and database schema to
ActivityPub entities, as this makes things easier to deal with.

We store received activities payload directly in the database before we attempt to process
or deliver them. Storing the activities unlock some interesting use cases, such as
debugging federation issues, replaying deliveries, or reprocess historical
activities that were not supported before.

Each local user is bound to an ``Actor``. Remote and local actors share the same
database table and all federated entities (such as uploads) are linked to an ``Actor``
and not to a user. This means that, internally, in general, there is no distinction between
local and remote users.

Links:

- `Federation models <https://code.eliotberriot.com/funkwhale/funkwhale/blob/develop/api/funkwhale_api/federation/models.py>`_


Activity creation and delivery
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a local actor is making an action that should trigger an ``Activity``, which roughly is equivalent
to posting an activity to an outbox, we create an object, with the proper payload and store it in our
``Activity`` table. We then trigger two kind of deliveries:

1. A delivery to local recipients: for each local recipient, we create an ``InboxItem``, linked to the activity. A local
   actor's feed is then made of all the available inbox items, which can also have a read/unread
   status
2. A delivery to remote recipients: we collect all inboxes and shared inbox urls from remote recipients,
   and create a ``Delivery`` object in our database, linked to the initial activity and the inbox or shared inbox url.
   This ``Delivery`` object is then used by our worker to post the activity content to the url.

Receiving an activity from a remote actor in a local inbox is basically the same, but we skip step 2.

Funkwhale does not support all activities, and we have a basic routing logic to handle
specific activities, and discard unsupported ones. Unsupported activities are still
received and stored though.

If a delivered activity matches one of our routes, a dedicated handler is called,
which can trigger additionnal logic. For instance, if we receive a :ref:`activity-create` activity
for an :ref:`object-audio` object, our handler will persist the proper data in our local ``Upload``
table, retrieve the audio cover, etc.

Links:

- `Routing logic for activities <https://code.eliotberriot.com/funkwhale/funkwhale/blob/develop/api/funkwhale_api/federation/routes.py>`_
- `Delivery logic for activities <https://code.eliotberriot.com/funkwhale/funkwhale/blob/develop/api/funkwhale_api/federation/tasks.py>`_


Supported activities
--------------------

.. _activity-follow:

Follow
^^^^^^

Supported on
************

- :ref:`object-Library` objects

Example of library follow
*************************

.. code-block:: json

  {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
        {}
    ],
    "type": "Follow",
    "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded",
    "actor": "https://music.rocks/federation/actors/Alice",
    "to": ["https://awesome.music/federation/actors/Bob"],
    "object": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6"
  }

In this example, Alice is following the :ref:`object-library` described in ``object``, which is
owned by Bob.

Internal logic
**************

When a follow is received on a :ref:`object-Library`, Funkwhale will behave differently
depending on the visibility of the library:

- Automatic accept, when the library is public: a notification is sent to the library owner, and an :ref:`activity-accept` is sent automatically to the follow actor.
- Manual accept, in all other cases: a notification is sent to the library owner. After manual approval from the owner, an :ref:`activity-accept` is sent to the follow actor.

Funkwhale uses library follow status to grant access to the follow actor. If a library
is not public and an actor does not have an approved follow, library content will be
inaccessible to the actor.

Checks
******

Before handling the activity, Funkwhale will ensure the library's owner is
the activity recipient.

.. _activity-accept:

Accept
^^^^^^

Supported on
************

- :ref:`activity-follow` objects

Example
*******

.. code-block:: json

  {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/v1",
      {}
    ],
    "type": "Accept",
    "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded/accept",
    "to": ["https://music.rocks/federation/actors/Alice"],
    "actor": "https://awesome.music/federation/actors/Bob",
    "object": {
      "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded",
      "type": "Follow",
      "actor": "https://music.rocks/federation/actors/Alice",
      "object": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
    },
  }

In this example, Bob accepts Alice's follow.

Internal logic
**************

When an :ref:`activity-accept` is received with a :ref:`activity-follow` object, the corresponding follow
is marked as accepted in the database.

For library follows, this means that the actor will receive future
activities occuring within this library, such as :ref:`activity-create` :ref:`object-audio`,
:ref:`activity-delete` :ref:`object-audio` or :ref:`activity-delete` :ref:`object-library`

The follow actor will also be able to browse the library pages and download the library's
audio files. Have a look at :ref:`library-access` for more details.


Checks
******

Before handling the activity, Funkwhale will ensure the accept comes from
the library's owner.

.. _activity-undo:

Undo
^^^^

Supported on
************

- :ref:`activity-follow` objects

Example
*******

.. code-block:: json

  {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/v1",
      {}
    ],
    "type": "Undo",
    "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded/accept",
    "to": ["https://awesome.music/federation/actors/Bob"],
    "actor": "https://music.rocks/federation/actors/Alice",
    "object": {
      "id": "https://music.rocks/federation/actors/Alice#follows/99fc40d7-9bc8-4c4a-add1-f637339e1ded",
      "type": "Follow",
      "actor": "https://music.rocks/federation/actors/Alice",
      "object": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
    },
  }

In this example, Alice is notifying Bob she's undoing her follow.

Internal logic
**************

When an undo is received, the corresponding follow is deleted from the database.

Checks
******

Before handling the activity, Funkwhale will ensure the undo actor is the
follow actor.

.. _activity-create:

Create
^^^^^^

Supported on
************

- :ref:`object-audio` objects

Example
*******

.. code-block:: json

  {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/v1",
      {}
    ],
    "to": [
      "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers"
    ],
    "type": "Create",
    "actor": "https://awesome.music/federation/actors/Bob",
    "object": {}
  }

.. note::

  Refer to :ref:`object-audio` to see the structure of the ``object`` attribute.

Internal logic
**************

When a :ref:`activity-create` is received with an :ref:`object-audio` object, Funkwhale will persist
a local upload and bind it to the proper library and track. If no local track
match the audio metadata, a track is created using the ``metadata`` attribute
from the :ref:`object-audio` object.

Checks
******

Before handling the activity, Funkwhale will ensure the activity actor and
the audio library's actor are the same.

If no local actor follows the audio's library, the activity will be discarded.

.. _activity-delete:

Delete
^^^^^^

Supported on
************

- :ref:`object-audio` objects
- :ref:`object-Library` objects

Example (on :ref:`object-Library`)
************************

.. code-block:: json

  {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/v1",
      {}
    ],
    "type": "Delete",
    "to": [
      "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers"
    ],
    "actor": "https://awesome.music/federation/actors/Bob",
    "object": {
      "type": "Library",
      "id": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6"
    }
  }

Example (on :ref:`object-audio`)
**********************

.. code-block:: json

  {
    "@context": [
      "https://www.w3.org/ns/activitystreams",
      "https://w3id.org/security/v1",
      {}
    ],
    "type": "Delete",
    "to": [
      "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers"
    ],
    "actor": "https://awesome.music/federation/actors/Bob",
    "object": {
      "type": "Audio",
      "id": [
        "https://awesome.music/federation/music/uploads/19420073-3572-48a9-8c6c-b385ee1b7905",
        "https://awesome.music/federation/music/uploads/11d99680-23c6-4f72-997a-073b980ab204",
        "https://awesome.music/federation/music/uploads/1efadc1c-a704-4b8a-a71a-b288b1d1f423"
      ]
    }
  }

In this example, Bob notifies the followers of their library that 3 objects were deleted.

.. note::

  For performance reason, when deleting :ref:`object-audio` objects, Funkwhale supports
  either a list of ids or a single id.

Internal logic
**************

When a :ref:`activity-delete` is received, the corresponding objects are immediately deleted
from the database.

Checks
******

Before handling deletion, Funkwhale ensures the actor initiating the activity
is the owner of the deleted :ref:`object-audio` or :ref:`object-Library`.

Supported objects
-----------------

.. _object-artist:

Artist
^^^^^^

.. note::

  This object is not standard.

Example
*******

.. code-block:: json

  {
    "type": "Artist",
    "id": "https://awesome.music/federation/music/artists/73c32807-a199-4682-8068-e967f734a320",
    "name": "Metallica",
    "published": "2018-04-08T12:19:05.920415+00:00",
    "musicbrainzId": "65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab"
  }

Structure
*********

- **id** (required): a uri identifying the artist over federation
- **name** (required): a name for the artist
- **published** (required): the publication date of the artist (on the federation)
- **musicbrainzId** (optional): the musicbrainz artist id

.. _object-album:

Album
^^^^^

.. note::

  This object is not standard.

Example
*******

.. code-block:: json

  {
    "type": "Album",
    "id": "https://awesome.music/federation/music/albums/69d488b5-fdf6-4803-b47c-9bb7098ea57e",
    "name": "Ride the Lightning",
    "released": "1984-01-01",
    "published": "2018-10-02T19:49:17.412546+00:00",
    "musicbrainzId": "589ff96d-0be8-3f82-bdd2-299592e51b40",
    "cover": {
      "href": "https://awesome.music/media/albums/covers/2018/10/02/b69d398b5-fdf6-4803-b47c-9bb7098ea57e.jpg",
      "type": "Link",
      "mediaType": "image/jpeg"
    },
    "artists": [
      {}
    ]
  }

Structure
*********

- **id** (required): a uri identifying the album over federation
- **name** (required): the title of the album
- **artists** (required): a list of :ref:`object-artist` objects involved in the album
- **published** (required): the publication date of the entity (on the federation)
- **released** (optional): the release date of the album
- **musicbrainzId** (optional): the musicbrainz release id
- **cover** (optional): a `Link` object representing the album cover

.. _object-track:

Track
^^^^^

.. note::

  This object is not standard.

Example
*******

.. code-block:: json

  {
    "type": "Track",
    "id": "https://awesome.music/federation/music/tracks/82ece296-6397-4e26-be90-bac5f9990240",
    "name": "For Whom the Bell Tolls",
    "position": 3,
    "published": "2018-10-02T19:49:35.822537+00:00",
    "musicbrainzId": "771ab043-8821-44f9-b8e0-2733c3126c6d",
    "artists": [
      {}
    ],
    "album": {}
  }

Structure
*********

- **id** (required): a uri identifying the track over federation
- **name** (required): the title of the track
- **position** (required): the position of the :ref:`object-track` in the album
- **published** (required): the publication date of the entity (on the federation)
- **musicbrainzId** (optional): the musicbrainz recording id
- **album** (required): the :ref:`object-album` that contains the track
- **artists** (required): a list of :ref:`object-artist` objects involved in the track (they can differ from the album artists)

.. _object-library:

Library
^^^^^^^

.. note::

  This object is not standard but inherits its behaviour and properties from
  Actor and Collection.


Example
*******

.. code-block:: json

  {
    "type": "Library",
    "id": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
    "actor": "https://awesome.music/federation/actors/MyNameIsTroll",
    "name": "My awesome library",
    "followers": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6/followers",
    "summary": "This library is for restricted use only",
    "totalItems": 4234,
    "first": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6?page=1",
    "last": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6?page=56",
  }


Structure
*********

- **id** (required): a uri identifying the library over federation
- **actor** (required): the id of the actor managing the library
- **name** (required): the name of the library
- **followers** (required): the id of the library's followers collection
- **totalItems** (required): the number of audio objects available in the library
- **first** (required): the URL of the first page of the library
- **last** (required): the URL of the last page of the library
- **summary** (optional): a description for the library

.. note::

  Crawling library pages requires authentication and an approved follow, unless the library is
  public.

.. _object-audio:

Audio
^^^^^

.. note::

  This object `is specified in ActivityStreams <https://www.w3.org/TR/activitystreams-vocabulary/#dfn-audio>`_,
  but Funkwhale needs non-standard attributes to handle it.

Example
*******

.. code-block:: json

  {
    "type": "Audio",
    "id": "https://awesome.music/federation/music/uploads/88f0bc20-d7fd-461d-a641-dd9ac485e096",
    "name": "For Whom the Bell Tolls - Ride the Lightning - Metallica",
    "size": 8656581,
    "bitrate": 320000,
    "duration": 213,
    "library": "https://awesome.music/federation/music/libraries/dc702491-f6ce-441b-9da0-cecbed08bcc6",
    "updated": "2018-10-02T19:49:35.646372+00:00",
    "published": "2018-10-02T19:49:35.646359+00:00",
    "track": {},
    "url": {
      "href": "https://awesome.music/api/v1/listen/82ece296-6397-4e26-be90-bac5f9990240/?upload=88f0bc20-d7fd-461d-a641-dd9ac485e096",
      "type": "Link",
      "mediaType": "audio/mpeg"
    }
  }

Structure
*********

- **id** (required): a uri identifying the audio over federation
- **name** (required): a human-friendly title for the audio (We concatenate track name, album title and artist name)
- **size** (required, non-standard): the size of the audio, in bytes
- **bitrate** (required, non-standard): the bitrate of the audio, in bytes/s
- **duration** (required): the duration of the audio, in seconds
- **library** (required, non-standard): the id of the :ref:`object-Library` object that contains the object
- **published** (required): the publication date of the entity (on the federation)
- **updated** (required): the last update date of the entity (on the federation)
- **url** (required): a ``Link`` object with an ``audio/`` mediaType where the audio file is downloadable
- **track** (required, non-standard): the :ref:`object-track` the :ref:`object-audio` is bound to

.. note::

  Accessing the Audio file via its url requires authentication and an approved follow on the containing library,
  unless the library is public.


.. _library-access:

Audio fetching on restricted libraries
--------------------------------------

:ref:`object-library` and :ref:`object-audio` url objects may require additional authentication
to be accessed.

For :ref:`object-library` objects:

- If the library is public, library pages can be accessed without restriction
- Otherwise, the HTTP request must be signed by an actor with an approved follow on the library


For :ref:`object-audio` url objects:

- If the audio's library is public, audio file can be accessed without restriction
- Otherwise, the HTTP request must be signed by an actor with an approved follow on the audio's library
