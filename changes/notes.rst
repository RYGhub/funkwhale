Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

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

