Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.


Allow-list to restrict federation to trusted domains
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Allow-Listing feature grants pod moderators
and administrators greater control over federation
by allowing you to create a pod-wide allow-list.

When allow-listing is enabled, your pod's users will only
be able to interact with pods included in the allow-list.
Any messages, activity, uploads, or modifications to
libraries and playlists will only be shared with pods
on the allow-list. Pods which are not included in the
allow-list will not have access to your pod's content
or messages and will not be able to send anything to
your pod.

If you want to enable this feature on your pod, or learn more, please refer to `our documentation <https://docs.funkwhale.audio/moderator/listing.html>`_!

Replaced Daphne by Gunicorn/Uvicorn [manual action required, non-docker only]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To improve the performance, stability and reliability of Funkwhale's web processes,
we now recommend using Gunicorn and Uvicorn instead of Daphne. This combination unlock new use cases such as:

- zero-downtime upgrades
- configurable number of web worker processes

Based on our benchmarks, Gunicorn/Unicorn is also faster and more stable under higher workloads compared to Daphne.

To benefit from this enhancement on existing instances, you need to add ``FUNKWHALE_WEB_WORKERS=1`` in your ``.env`` file
(use a higher number if you want to have more web worker processes).

Then, edit your ``/etc/systemd/system/funkwhale-server.service`` and replace the ``ExecStart=`` line with
``ExecStart=/srv/funkwhale/virtualenv/bin/gunicorn config.asgi:application -w ${FUNKWHALE_WEB_WORKERS} -k uvicorn.workers.UvicornWorker -b ${FUNKWHALE_API_IP}:${FUNKWHALE_API_PORT}``

Then reload the configuration change with ``sudo systemctl daemon-reload`` and ``sudo systemctl restart funkwhale-server``.


Content-Security-Policy and additional security headers [manual action suggested]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To improve the security and reduce the attack surface in case of a successfull exploit, we suggest
you add the following Content-Security-Policy to your nginx configuration.

**On non-docker setups**, in ``/etc/nginx/sites-available/funkwhale.conf``::

    server {

        add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
        add_header Referrer-Policy "strict-origin-when-cross-origin";

        location /front/ {
            add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
            add_header Referrer-Policy "strict-origin-when-cross-origin";
            add_header X-Frame-Options "SAMEORIGIN";
            # … existing content here
        }

        # Also create a new location for the embeds to ensure external iframes work
        # Simply copy-paste the /front/ location, but replace the following lines:
        location /front/embed.html {
            add_header X-Frame-Options "ALLOW";
            alias ${FUNKWHALE_FRONTEND_PATH}/embed.html;
        }
    }

Then reload nginx with ``systemctl reload nginx``.

**On docker setups**, in ``/srv/funkwhalenginx/funkwhale.template``::

    server {

        add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
        add_header Referrer-Policy "strict-origin-when-cross-origin";

        location /front/ {
            add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self' data:; object-src 'none'; media-src 'self' data:";
            add_header Referrer-Policy "strict-origin-when-cross-origin";
            add_header X-Frame-Options "SAMEORIGIN";
            # … existing content here
        }

        # Also create a new location for the embeds to ensure external iframes work
        # Simply copy-paste the /front/ location, but replace the following lines:
        location /front/embed.html {
            add_header X-Frame-Options "ALLOW";
            alias /frontent/embed.html;
        }
    }

Then reload nginx with ``docker-compose restart nginx``.
