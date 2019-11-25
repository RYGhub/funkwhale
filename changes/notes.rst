Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.

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
