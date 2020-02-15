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

Postgres docker changed environment variable [manual action required, docker only]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you're running with docker and our multi-container setup, there was a breaking change starting in the 11.7 postgres image (https://github.com/docker-library/postgres/pull/658)

You need to add this to your .env file: ``POSTGRES_HOST_AUTH_METHOD=trust``

Newer deployments aren't affected.
