Allow embedding of albums and tracks available in public libraries via an <iframe> (#578)

Iframe widget to embed public tracks and albums [manual action required]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
        alias /frontend;
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
        alias ${FUNKWHALE_FRONTEND_PATH};
    }

Replace ``${FUNKWHALE_FRONTEND_PATH}`` by the corresponding variable from your .env file,
which should be ``/srv/funkwhale/front/dist`` by default, then reload your nginx process with
``sudo systemctl reload nginx``.
