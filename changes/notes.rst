Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

Channels and podcasts
^^^^^^^^^^^^^^^^^^^^^

Funkwhale 0.21 includes a brand new feature: Channels!

Channels can be used as a replacement to public libraries,
to publish audio content, both musical and non-musical. They federate with other Funkwhale pods, but also other
fediverse software, in particular Mastodon, Pleroma, Friendica and Reel2Bits, meaning people can subscribe to your channel
from any of these software. To get started with publication, simply visit your profile and create a channel from there.

Each Funkwhale channel also comes with RSS feed that is compatible with existing podcasting applications, like AntennaPod
on Android and, within Funkwhale, you can also subscribe to any podcast from its RSS feed!

Many, many thanks to the numerous people who helped with the feature design, development and testing, and in particular
to the members of the working group who met every week for months in order to get this done.

Redesigned navigation, player and queue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This release includes a full redesign of our navigation, player and queue. Overall, it should provide
a better, less confusing experience, especially on mobile devices. This redesign was suggested
14 months ago, and took a while, but thanks to the involvement and feedback of many people, we got it done!

Improved search bar for searching remote objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The search bar now support fetching arbitrary objects using a URL. In particular, you can use this to quickly:

- Subscribe to a remote library via its URL
- Listen a public track from another pod
- Subscribe to a channel

Screening for sign-ups and custom sign-up form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instance admins can now configure their pod so that registrations required manual approval from a moderator. This
is especially useful on private or semi-private pods where you don't want to close registrations completely,
but don't want spam or unwanted users to join your pod.

When this is enabled and a new user register, their request is put in a moderation queue, and moderators
are notified by email. When the request is approved or refused, the user is also notified by email.

In addition, it's also possible to customize the sign-up form by:

- Providing a custom help text, in markdown format
- Including additional fields in the form, for instance to ask the user why they want to join. Data collected through these fields is included in the sign-up request and viewable by the mods

Federated reports
^^^^^^^^^^^^^^^^^

It's now possible to send a copy of a report to the server hosting the reported object, in order to make moderation easier and more distributed.

This feature is inspired by Mastodon's current design, and should work with at least Funkwhale and Mastodon servers.

Improved search performance
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Our search engine went through a full rewrite to make it faster. This new engine is enabled
by default when using the search bar, or when searching for artists, albums and tracks. It leverages
PostgreSQL full-text search capabilities.

During our tests, we observed huge performance improvements after the switch, by an order of
magnitude. This should be especially perceptible on pods with large databases, more modest hardware
or hard drives.

We plan to remove the old engine in an upcoming release. In the meantime, if anything goes wrong,
you can switch back by setting ``USE_FULL_TEXT_SEARCH=false`` in your ``.env`` file.

Enforced email verification
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The brand new ``ACCOUNT_EMAIL_VERIFICATION_ENFORCE`` setting can be used to make email verification
mandatory for your users. It defaults to ``false``, and doesn't apply to superuser accounts created through
the CLI.

If you enable this, ensure you have a SMTP server configured too.

User management through the server CLI
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We now support user creation (incl. non-admin accounts), update and removal directly
from the server CLI. Typical use cases include:

- Changing a user password from the command line
- Creating or updating users from deployments scripts or playbooks
- Removing or granting permissions or upload quota to multiple users at once
- Marking multiple users as inactive

All user-related commands are available under the ``python manage.py fw users`` namespace.
Please refer to the `Admin documentation <https://docs.funkwhale.audio/admin/commands.html#user-management>`_ for
more information and instructions.

Progressive web app [Manual change suggested, non-docker only]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We've made Funkwhale's Web UI a Progressive Web Application (PWA), in order to improve the user experience
during offline use, and on mobile devices.

In order to fully benefit from this change, if your pod isn't deployed using Docker, ensure
the following instruction is present in your nginx configuration::

    location /front/ {
        # Add the following line in the /front/ location
        add_header Service-Worker-Allowed "/";
    }

Postgres docker changed environment variable [manual action required, docker multi-container only]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're running with docker and our multi-container setup, there was a breaking change starting in the 11.7 postgres image (https://github.com/docker-library/postgres/pull/658)

You need to add this to your .env file: ``POSTGRES_HOST_AUTH_METHOD=trust``

Newer deployments aren't affected.

Upgrade from Postgres 10 to 11 [manual action required, docker all-in-one only]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With our upgrade to Alpine 3.10, the ``funkwhale/all-in-one`` image now includes PostgreSQL 11.

In order to update to Funkwhale 0.21, you will first need to uprade Funkwhale's PostgreSQL database, following the steps below::

    # open a shell as the Funkwhale user
    sudo -u funkwhale -H bash

    # move to the funkwhale data directory
    # (replace this with your own if you used a different path)
    cd /srv/funkwhale/data

    # stop the funkwhale container
    docker stop funkwhale

    # backup the database files
    cp -r data/ ../postgres.bak

    # Upgrade the database
    docker run --rm \
        -v $(pwd)/data:/var/lib/postgresql/10/data \
        -v $(pwd)/upgraded-postgresql:/var/lib/postgresql/11/data \
        -e PGUSER=funkwhale \
        -e POSTGRES_INITDB_ARGS="-U funkwhale --locale C --encoding UTF8" \
        tianon/postgres-upgrade:10-to-11

    # replace the Postgres 10 files with Postgres 11 files
    mv data/ postgres-10
    mv upgraded-postgresql/ data

Once you have completed the Funkwhale upgrade with our regular instructions and everything works properly,
you can remove the backups/old files::

    sudo -u funkwhale -H bash
    cd /srv/funkwhale/data
    rm -rf ../postgres.bak
    rm -rf postgres-10
