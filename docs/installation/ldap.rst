LDAP configuration
==================

LDAP is a protocol for providing directory services, in practice allowing a central authority for user login information.

Funkwhale supports LDAP through the Django LDAP authentication module and by setting several configuration options.

.. warning::

    Note the following restrictions when using LDAP:

        * LDAP-based users cannot change passwords inside the app.

Dependencies
------------

LDAP support requires some additional dependencies to enable. On the OS level both ``libldap2-dev`` and ``libsasl2-dev`` are required, and the Python modules ``python-ldap`` and ``python-django-auth-ldap`` must be installed. These dependencies are all included in the ``requirements.*`` files so deploying with those will install these dependencies by default. However, they are not required unless LDAP support is explicitly enabled.

Environment variables
---------------------

LDAP authentication is configured entirely through the environment variables. The following options enable the LDAP features:

Basic features:

* ``LDAP_ENABLED``: Set to ``True`` to enable LDAP support. Default: ``False``.
* ``LDAP_SERVER_URI``: LDAP URI to the authentication server, e.g. ``ldap://my.host:389``.
* ``LDAP_BIND_DN``: LDAP user DN to bind as to perform searches.
* ``LDAP_BIND_PASSWORD``: LDAP user password for bind DN.
* ``LDAP_SEARCH_FILTER``: The LDAP user filter, using ``{0}`` as the username placeholder, e.g. ``(|(cn={0})(mail={0}))``; uses standard LDAP search syntax. Default: ``(uid={0})``.
* ``LDAP_START_TLS``: Set to ``True`` to enable LDAP StartTLS support. Default: ``False``.
* ``LDAP_ROOT_DN``: The LDAP search root DN, e.g. ``dc=my,dc=domain,dc=com``; supports multiple entries in a space-delimited list, e.g. ``dc=users,dc=domain,dc=com dc=admins,dc=domain,dc=com``.
* ``LDAP_USER_ATTR_MAP``: A mapping of Django user attributes to LDAP values, e.g. ``first_name:givenName, last_name:sn, username:cn, email:mail``. Default: ``first_name:givenName, last_name:sn, username:cn, email:mail``.

Group features:

For details on these options, see `the Django documentation <https://django-auth-ldap.readthedocs.io/en/latest/groups.html>`_. Group configuration is disabled unless an ``LDAP_GROUP_DN`` is set. This is an advanced LDAP feature and most users should not need to configure these settings.

* ``LDAP_GROUP_DN``: The LDAP group search root DN, e.g. ``ou=groups,dc=domain,dc=com``.
* ``LDAP_GROUP_FILTER``: The LDAP group filter, e.g. ``(objectClass=groupOfNames)``.
* ``LDAP_REQUIRE_GROUP``: A group users must be a part of to authenticate, e.g. ``cn=enabled,ou=groups,dc=domain,dc=com``.
* ``LDAP_DENY_GROUP``: A group users must not be a part of to authenticate, e.g. ``cn=disabled,ou=groups,dc=domain,dc=com``.
