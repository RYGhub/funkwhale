Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

Redesigned navigation, player and queue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This release includes a full redesign of our navigation, player and queue. Overall, it should provide
a better, less confusing experience, especially on mobile devices. This redesign was suggested
14 months ago, and took a while, but thanks to the involvement and feedback of many people, we got it done!

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
