Changelog
=========

0.2
-------

2017-07-09

* [feature] can now import artist and releases from youtube and musicbrainz.
  This requires a YouTube API key for the search
* [breaking] we now check for user permission before serving audio files, which requires
a specific configuration block in your reverse proxy configuration:

.. code-block::

    location /_protected/media {
        internal;
        alias   /srv/funkwhale/data/media;
    }



0.1
-------

2017-06-26

Initial release
