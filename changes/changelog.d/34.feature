Switched to django-channels and daphne for serving HTTP and websocket (#34)

Upgrade notes
^^^^^^^^^^^^^

This release include an important change in the way we serve the HTTP API.
To prepare for new realtime features and enable websocket support in Funkwhale,
we are now using django-channels and daphne to serve HTTP and websocket traffic.

This replaces gunicorn and the switch should be easy assuming you
follow the upgrade process described bellow.

If you are using docker, please remove the command instruction inside the
api service, as the up-to-date command is now included directly in the image
as the default entry point:

.. code-block:: yaml

    api:
      restart: unless-stopped
      image: funkwhale/funkwhale:${FUNKWHALE_VERSION:-latest}
      command: ./compose/django/gunicorn.sh  # You can remove this line

On non docker setups, you'll have to update the [Service] block of your
funkwhale-server systemd unit file to launch the application server using daphne instead of gunicorn.

The new configuration should be similar to this:

.. code-block:: ini

    [Service]
    User=funkwhale
    # adapt this depending on the path of your funkwhale installation
    WorkingDirectory=/srv/funkwhale/api
    EnvironmentFile=/srv/funkwhale/config/.env
    ExecStart=/usr/local/bin/daphne -b ${FUNKWHALE_API_IP} -p ${FUNKWHALE_API_PORT} config.asgi:application

Ensure you update funkwhale's dependencies as usual to install the required
packages.

On both docker and non-docker setup, you'll also have to update your nginx
configuration for websocket support. Ensure you have the following blocks
included in your virtualhost file:

.. code-block:: txt

    map $http_upgrade $connection_upgrade {
        default upgrade;
        ''      close;
    }

    server {
        ...
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }

Remember to reload your nginx server after the edit.
