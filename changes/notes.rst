Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

Fix Gzip compression to avoid BREACH exploit [security] [manual action required]
--------------------------------------------------------------------------------

In the 0.18 release, we've enabled Gzip compression by default for various
content types, including HTML and JSON. Unfortunately, enabling Gzip compression
on such content types could make BREACH-type exploits possible.

We've removed the risky content-types from our nginx template files, to ensure new
instances are safe, however, if you already have an instance, you need
to double check that your host nginx virtualhost do not include the following
values for the ``gzip_types`` settings::

   application/atom+xml
   application/json
   application/ld+json
   application/activity+json
   application/manifest+json
   application/rss+xml
   application/xhtml+xml
   application/xml

For convenience, you can also replace the whole setting with the following snippet::

   gzip_types
      application/javascript
      application/vnd.geo+json
      application/vnd.ms-fontobject
      application/x-font-ttf
      application/x-web-app-manifest+json
      font/opentype
      image/bmp
      image/svg+xml
      image/x-icon
      text/cache-manifest
      text/css
      text/plain
      text/vcard
      text/vnd.rim.location.xloc
      text/vtt
      text/x-component
      text/x-cross-domain-policy;


Fix Apache configuration file for 0.18 [manual action required]
----------------------------------------------------------

The way front is served has changed since 0.18. The Apache configuration can't serve 0.18 properly, leading to blank screens.

If you are on an Apache setup, you will have to replace the `<Location "/api">` block with the following::

   <Location "/">
      # similar to nginx 'client_max_body_size 100M;'
      LimitRequestBody 104857600

      ProxyPass ${funkwhale-api}/
      ProxyPassReverse ${funkwhale-api}/
   </Location>

And add some more `ProxyPass` directives so that the `Alias` part of your configuration file looks this way::

   ProxyPass "/front" "!"
   Alias /front /srv/funkwhale/front/dist

   ProxyPass "/media" "!"
   Alias /media /srv/funkwhale/data/media

   ProxyPass "/staticfiles" "!"
   Alias /staticfiles /srv/funkwhale/data/static

In case you are using custom css and theming, you also need to match this block::

   ProxyPass "/settings.json" "!"
   Alias /settings.json /srv/funkwhale/custom/settings.json

   ProxyPass "/custom" "!"
   Alias /custom /srv/funkwhale/custom
