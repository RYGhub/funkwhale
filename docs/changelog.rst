Changelog
=========

next
-------

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
