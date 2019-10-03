Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.


Support for genres via tags
^^^^^^^^^^^^^^^^^^^^^^^^^^^

One of our most requested missing features is now available!

Starting with Funkwhale 0.20,
Funkwhale will automatically extract genre information from uploaded files and associate it
with the corresponding tracks in the form of tags (similar to Mastodon or Twitter hashtags).
Please refer to `our tagging documentation <https://docs.funkwhale.audio/users/upload.html#tagging-files>`_
for more information regarding the tagging process.

Tags can also be associated with artists and albums, and updated after upload through the UI using
the edit system released in Funkwhale 0.19. Tags are also fetched when retrieving content
via federation.

Tags are used in various places to enhance user experience:

- Tags are listed on tracks, albums and artist profiles
- Each tag has a dedicated page were you can browse corresponding content and quickly start a radio
- The custom radio builder now supports using tags
- Subsonic apps that support genres - such as DSub or Ultrasonic - should display this information as well

If you are a pod admin and want to extract tags from already uploaded content, you run `this snippet <https://dev.funkwhale.audio/funkwhale/funkwhale/snippets/43>`_
and `this snippet <https://dev.funkwhale.audio/funkwhale/funkwhale/snippets/44>`_ in a ``python manage.py shell``.

Content and account reports
^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is now possible to report content, such as artists, tracks or libraries, as well as user accounts. Such reports are forwarded to the pod moderators,
who can review it and delete reported content, block accounts or take any other action they deem necessary.

By default, both anonymous and authenticated users can submit these reports. This makes sure moderators can receive and handle
takedown requests and other reports for illegal content that may be sent by third-parties without an account on the pod. However,
you can disable anonymous reports completely via your pod settings.

Federation of the reports will be supported in a future release.

For more information about this feature, please check out our documentation:

-  `User documentation <https://docs.funkwhale.audio/moderator/reports.html>`_
-  `Moderator documentation <https://docs.funkwhale.audio/users/reports.html>`_

Account deletion
^^^^^^^^^^^^^^^^

Users can now delete their account themselves, without involving an administrator.

The deletion process will remove any local data and objects associated with the account,
but the username won't be able to new users to avoid impersonation. Deletion is also broadcasted
to other known servers on the federation.

For more information about this feature, please check out our documentation:

-  `User documentation <https://docs.funkwhale.audio/users/account.html>`_

Landing and about page redesign [Manual action suggested]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In this release, we've completely redesigned the landing and about page, by making it more useful and adapted to your pod
configuration. Among other things, the landing page will now include:

- your pod and an excerpt from your pod's description
- your pod banner image, if any
- your contact email, if any
- the login form
- the signup form (if registrations are open on your pod)
- some basic statistics about your pod
- a widget including recently uploaded albums, if anonymous access is enabled

The landing page will still include some information about Funkwhale, but in a less intrusive and proeminent way than before.

Additionally, the about page now includes:

- your pod name, description, rules and terms
- your pod banner image, if any
- your contact email, if any
- comprehensive statistics about your pod
- some info about your pod configuration, such as registration and federation status or the default upload quota for new users

With this redesign, we've added a handful of additional pod settings:

- Pod banner image
- Contact email
- Rules
- Terms of service

We recommend taking a few moments to fill these accordingly to your needs, by visiting ``/manage/settings``.

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

Periodic message to incite people to support their pod and Funkwhale
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Users will now be reminded on a regular basis that they can help Funkwhale by donating or contributing.

If specified by the pod admin, a separate and custom message will also be displayed in a similar way to provide instructions and links to support the pod.

Both messages will appear for the first time 15 days after signup, in the notifications tab. For each message, users can schedule a reminder for a later time, or disable the messages entirely.


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

..note::

    If you are using an S3-compatible store to serve music, you will need to specify the URL of your S3 store in the ``media-src`` and ``img-src`` headers

    .. code-block::

        add_header Content-Security-Policy "...img-src 'self' https://<your-s3-URL> data:;...media-src https://<your-s3-URL> 'self' data:";

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

Rate limiting
^^^^^^^^^^^^^

With this release, rate-limiting on the API is enabled by default, with high enough limits to ensure
regular users of the app aren't affected. Requests beyond allowed limits are answered with a 429 HTTP error.

For anonymous requests, the limit is applied to the IP adress of the client, and for authenticated requests, the limit
is applied to the corresponding user account. By default, anonymous requests get a lower limit than authenticated requests.

You can disable the rate-limiting feature by adding `THROTTLING_ENABLED=false` to your ``.env`` file and restarting the
services. If you are using the Funkwhale API in your project or app and want to know more about the limits, please consult https://docs.funkwhale.audio/swagger/.

Broken audio streaming when using S3/Minio and DSub [manual action required]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some Subsonic clients, such as DSub, are sending an Authorization headers which was forwarded
to the S3 storage when streaming, causing some issues. If you are using S3 or a compatible storage
such as Minio, please add the following in your nginx ``~ /_protected/media/(.+)`` location::

    # Needed to ensure DSub auth isn't forwarded to S3/Minio, see #932
    proxy_set_header Authorization "";

And reload your nginx process.
