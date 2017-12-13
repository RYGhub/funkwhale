Changelog
=========

0.2.1
-----

2017-07-17

* Now return media files with absolute URL
* Now display CLI instructions to download a set of tracks
* Fixed #33: sort by track position in album in API by default, also reuse that information on frontend side
* More robust audio player and queue in various situations:
* upgrade to latest dynamic_preferences and use redis as cache even locally


0.2
-------

2017-07-09

* [feature] can now import artist and releases from youtube and musicbrainz.
  This requires a YouTube API key for the search
* [breaking] we now check for user permission before serving audio files, which requires
  a specific configuration block in your reverse proxy configuration::

    location /_protected/media {
        internal;
        alias   /srv/funkwhale/data/media;
    }



0.1
-------

2017-06-26

Initial release
