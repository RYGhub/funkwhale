Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

Audio transcoding is back!
--------------------------

After removal of our first, buggy transcoding implementation, we're proud to announce
that this feature is back. It is enabled by default, and can be configured/disabled
in your instance settings!

This feature works in the browser, with federated/non-federated tracks and using Subsonic clients.
Transcoded tracks are generated on the fly, and cached for a configurable amount of time,
to reduce the load on the server.


Automatically load .env file
----------------------------

On non-docker deployments, earlier versions required you to source
the config/.env file before launching any Funkwhale command, with ``export $(cat config/.env | grep -v ^# | xargs)``
This led to more complex and error prode deployment / setup.

This is not the case anymore, and Funkwhale will automatically load this file if it's available.

Licensing and copyright information
-----------------------------------

Funkwhale is now able to parse copyright and license data from file and store
this information. Apart from displaying it on each track detail page,
no additional behaviour is currently implemented to use this new data, but this
will change in future releases.

License and copyright data is also broadcasted over federation.

License matching is done on the content of the ``License`` tag in the files,
with a fallback on the ``Copyright`` tag.

Funkwhale will successfully extract licensing data for the following licenses:

- Creative Commons 0 (Public Domain)
- Creative Commons 1.0 (All declinations)
- Creative Commons 2.0 (All declinations)
- Creative Commons 2.5 (All declinations and countries)
- Creative Commons 3.0 (All declinations and countries)
- Creative Commons 4.0 (All declinations)

Support for other licenses such as Art Libre or WTFPL will be added in future releases.


Enable gzip compression [manual action suggested]
-------------------------------------------------

Gzip compression will be enabled on new instances by default
and will reduce the amount of bandwidth consumed by your instance.

If you with to benefit from gzip compression on your instance,
edit your reverse proxy virtualhost file (located at ``/etc/nginx/sites-available/funkwhale.conf``) and add the following snippet
in the server block, then reload your nginx server::

    server {
        # ... exiting configuration

        # compression settings
        gzip on;
        gzip_comp_level    5;
        gzip_min_length    256;
        gzip_proxied       any;
        gzip_vary          on;

        gzip_types
            application/atom+xml
            application/javascript
            application/json
            application/ld+json
            application/activity+json
            application/manifest+json
            application/rss+xml
            application/vnd.geo+json
            application/vnd.ms-fontobject
            application/x-font-ttf
            application/x-web-app-manifest+json
            application/xhtml+xml
            application/xml
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
        # end of compression settings
    }

Instance-level moderation tools
-------------------------------

This release includes a first set of moderation tools that will give more control
to admins about the way their instance federate with other instance and accounts on the network.
Using these tools, it's now possible to:

- Browse known accounts and domains, and associated data (storage size, software version, etc.)
- Purge data belonging to given accounts and domains
- Block or partially restrict interactions with any account or domain

All those features are usable using a brand new "moderation" permission, meaning
you can appoints one or nultiple moderators to help with this task.

I'd like to thank all Mastodon contributors, because some of the these tools are heavily
inspired from what's being done in Mastodon. Thank you so much!


Iframe widget to embed public tracks and albums [manual action required]
------------------------------------------------------------------------

Funkwhale now support embedding a lightweight audio player on external websites
for album and tracks that are available in public libraries. Important pages,
such as artist, album and track pages also include OpenGraph tags that will
enable previews on compatible apps (like sharing a Funkwhale track link on Mastodon
or Twitter).

To achieve that, we had to tweak the way Funkwhale front-end is served. You'll have
to modify your nginx configuration when upgrading to keep your instance working.

**On docker setups**, edit your ``/srv/funkwhale/nginx/funkwhale.template`` and replace
the ``location /api/`` and `location /` blocks by the following snippets::

    location / {
        include /etc/nginx/funkwhale_proxy.conf;
        # this is needed if you have file import via upload enabled
        client_max_body_size ${NGINX_MAX_BODY_SIZE};
        proxy_pass   http://funkwhale-api/;
    }

    location /front/ {
        alias /frontend/;
    }

The change of configuration will be picked when restarting your nginx container.

**On non-docker setups**, edit your ``/etc/nginx/sites-available/funkwhale.conf`` file,
and replace the ``location /api/`` and `location /` blocks by the following snippets::


    location / {
        include /etc/nginx/funkwhale_proxy.conf;
        # this is needed if you have file import via upload enabled
        client_max_body_size ${NGINX_MAX_BODY_SIZE};
        proxy_pass   http://funkwhale-api/;
    }

    location /front/ {
        alias ${FUNKWHALE_FRONTEND_PATH}/;
    }

Replace ``${FUNKWHALE_FRONTEND_PATH}`` by the corresponding variable from your .env file,
which should be ``/srv/funkwhale/front/dist`` by default, then reload your nginx process with
``sudo systemctl reload nginx``.
