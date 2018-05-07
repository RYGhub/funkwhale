Use nodeinfo standard for publishing instance information (#192)

Nodeinfo standard for instance information and stats
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::

    The ``/api/v1/instance/stats/`` endpoint which was used to display
    instance data in the about page is removed in favor of the new
    ``/api/v1/instance/nodeinfo/2.0/`` endpoint.

In earlier version, we where using a custom endpoint and format for
our instance information and statistics. While this was working,
this was not compatible with anything else on the fediverse.

We now offer a nodeinfo 2.0 endpoint which provides, in a single place,
all the instance information such as library and user activity statistics,
public instance settings (description, registration and federation status, etc.).

We offer two settings to manage nodeinfo in your Funkwhale instance:

1. One setting to completely disable nodeinfo, but this is not recommended
   as the exposed data may be needed to make some parts of the front-end
   work (especially the about page).
2. One setting to disable only usage and library statistics in the nodeinfo
   endpoint. This is useful if you want the nodeinfo endpoint to work,
   but don't feel comfortable sharing aggregated statistics about your library
   and user activity.
 
To make your instance fully compatible with the nodeinfo protocol, you need to
to edit your nginx configuration file:

.. code-block::

    # before
    ...
    location /.well-known/webfinger {
        include /etc/nginx/funkwhale_proxy.conf;
        proxy_pass   http://funkwhale-api/.well-known/webfinger;
    }
    ...

    # after
    ...
    location /.well-known/ {
        include /etc/nginx/funkwhale_proxy.conf;
        proxy_pass   http://funkwhale-api/.well-known/;
    }
    ...

You can do the same if you use apache:

.. code-block::

    # before
    ...
    <Location "/.well-known/webfinger">
      ProxyPass ${funkwhale-api}/.well-known/webfinger
      ProxyPassReverse ${funkwhale-api}/.well-known/webfinger
    </Location>
    ...

    # after
    ...
    <Location "/.well-known/">
      ProxyPass ${funkwhale-api}/.well-known/
      ProxyPassReverse ${funkwhale-api}/.well-known/
    </Location>
    ...

This will ensure all well-known endpoints are proxied to funkwhale, and
not just webfinger one.

Links:

- About nodeinfo: https://github.com/jhass/nodeinfo
