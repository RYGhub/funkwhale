Subsonic API implementation to offer compatibility with existing clients such as DSub (#75)

Subsonic API
^^^^^^^^^^^^

This release implements some core parts of the Subsonic API, which is widely
deployed in various projects and supported by numerous clients.

By offering this API in Funkwhale, we make it possible to access the instance
library and listen to the music without from existing Subsonic clients, and
without developping our own alternative clients for each and every platform.

Most advanced Subsonic clients support offline caching of music files,
playlist management and search, which makes them well-suited for nomadic use.

Please head over :doc:`users/apps` for more informations about supported clients
and user instructions.

At the instance-level, the Subsonic API is enabled by default, but require
and additional endpoint to be added in you reverse-proxy configuration.

On nginx, add the following block::

    location /rest/ {
        include /etc/nginx/funkwhale_proxy.conf;
        proxy_pass   http://funkwhale-api/api/subsonic/rest/;
    }

On Apache, add the following block::

    <Location "/rest">
        ProxyPass ${funkwhale-api}/api/subsonic/rest
        ProxyPassReverse ${funkwhale-api}/api/subsonic/rest
    </Location>

The Subsonic can be disabled at the instance level from the django admin.

.. note::

    Because of Subsonic's API design which assumes cleartext storing of
    user passwords, we chose to have a dedicated, separate password
    for that purpose. Users can generate this password from their
    settings page in the web client.
