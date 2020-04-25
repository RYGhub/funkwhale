Instance configuration
======================

General configuration is achieved using two type of settings:
:ref:`environment variables <environment-variables>` and
:ref:`instance settings <instance-settings>`.

.. _environment-variables:

Environment variables
---------------------

Those are located in your ``.env`` file, which you should have created
during installation. A full list of available variables can be seen
:ref:`below <environment-variables>`.

Options from this file are heavily commented, and usually target lower level
and technical aspects of your instance, such as database credentials.

.. note::

    You should restart all Funkwhale processes when you change the values
    on environment variables.


.. note::

    Some characters are unsafe to use in configuration variables that are URLs,
    such as the user and password in the database and SMTP sections.
    If those variables contain such characters, they must be urlencoded, for
    instance using the following command:
    ``python3 -c 'import urllib.parse; print(urllib.parse.quote_plus("p@ssword"))``

    cf. https://github.com/joke2k/django-environ#using-unsafe-characters-in-urls

.. _instance-settings:

Instance settings
-----------------

These settings are stored in the database and do not require a restart of your
instance after modification. They typically relate to higher level configuration,
such your instance description, signup policy and so on.

You can edit those settings directly from the web application, assuming
you have the required permissions. The URL is ``/manage/settings``, and
you will also find a link to this page in the sidebar.

If you plan to use acoustid and external imports
(e.g. with the YouTube backends), you should edit the corresponding
settings in this interface.

.. note::

    If you have any issue with the web application, a management interface is also
    available for those settings from :doc:`Django's administration interface <django>`. It's
    less user friendly, though, and we recommend you use the web app interface
    whenever possible.

    The URL should be ``/api/admin/dynamic_preferences/globalpreferencemodel/`` (prepend your domain in front of it, of course).


Configuration reference
-----------------------

Pod
^^^

.. autodata:: config.settings.common.FUNKWHALE_HOSTNAME
    :annotation:
.. autodata:: config.settings.common.FUNKWHALE_PROTOCOL

Database and redis
^^^^^^^^^^^^^^^^^^

.. autodata:: config.settings.common.DATABASE_URL
    :annotation:
.. autodata:: config.settings.common.DB_CONN_MAX_AGE
.. autodata:: config.settings.common.CACHE_URL
    :annotation:
.. autodata:: config.settings.common.CELERY_BROKER_URL
    :annotation:

Accounts and registration
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: config.settings.common.ACCOUNT_EMAIL_VERIFICATION_ENFORCE
    :annotation:
.. autodata:: config.settings.common.USERS_INVITATION_EXPIRATION_DAYS
    :annotation:
.. autodata:: config.settings.common.DISABLE_PASSWORD_VALIDATORS
    :annotation:
.. autodata:: config.settings.common.ACCOUNT_USERNAME_BLACKLIST
    :annotation:
.. autodata:: config.settings.common.AUTH_LDAP_ENABLED
    :annotation:

Media storage and serving
^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: config.settings.common.MEDIA_URL
    :annotation: = https://mypod.audio/media/
.. autodata:: config.settings.common.MEDIA_ROOT
    :annotation: = /srv/funkwhale/data/media
.. autodata:: config.settings.common.PROXY_MEDIA
    :annotation: = true
.. autodata:: config.settings.common.EXTERNAL_MEDIA_PROXY_ENABLED
.. autodata:: config.settings.common.ATTACHMENTS_UNATTACHED_PRUNE_DELAY
    :annotation: = true
.. autodata:: config.settings.common.REVERSE_PROXY_TYPE
.. autodata:: config.settings.common.PROTECT_FILES_PATH

Audio acquisition
^^^^^^^^^^^^^^^^^

.. autodata:: config.settings.common.MUSIC_DIRECTORY_PATH
.. autodata:: config.settings.common.MUSIC_DIRECTORY_SERVE_PATH

S3 Storage
^^^^^^^^^^

.. autodata:: config.settings.common.AWS_QUERYSTRING_AUTH
.. autodata:: config.settings.common.AWS_QUERYSTRING_EXPIRE
.. autodata:: config.settings.common.AWS_ACCESS_KEY_ID
.. autodata:: config.settings.common.AWS_SECRET_ACCESS_KEY
.. autodata:: config.settings.common.AWS_STORAGE_BUCKET_NAME
.. autodata:: config.settings.common.AWS_S3_CUSTOM_DOMAIN
.. autodata:: config.settings.common.AWS_S3_ENDPOINT_URL
.. autodata:: config.settings.common.AWS_S3_REGION_NAME
.. autodata:: config.settings.common.AWS_LOCATION

API configuration
^^^^^^^^^^^^^^^^^

.. autodata:: config.settings.common.THROTTLING_ENABLED
.. autodata:: config.settings.common.THROTTLING_RATES
.. autodata:: config.settings.common.ADMIN_URL
.. autodata:: config.settings.common.EXTERNAL_REQUESTS_VERIFY_SSL
.. autodata:: config.settings.common.EXTERNAL_REQUESTS_TIMEOUT

Federation
^^^^^^^^^^

.. autodata:: config.settings.common.FEDERATION_OBJECT_FETCH_DELAY
.. autodata:: config.settings.common.FEDERATION_DUPLICATE_FETCH_DELAY

Metadata
^^^^^^^^

.. autodata:: config.settings.common.TAGS_MAX_BY_OBJ
.. autodata:: config.settings.common.MUSICBRAINZ_HOSTNAME
.. autodata:: config.settings.common.MUSICBRAINZ_CACHE_DURATION

Channels and podcasts
^^^^^^^^^^^^^^^^^^^^^

.. autodata:: config.settings.common.PODCASTS_RSS_FEED_REFRESH_DELAY
.. autodata:: config.settings.common.PODCASTS_RSS_FEED_MAX_ITEMS
.. autodata:: config.settings.common.PODCASTS_THIRD_PARTY_VISIBILITY

Subsonic
^^^^^^^^

.. autodata:: config.settings.common.SUBSONIC_DEFAULT_TRANSCODING_FORMAT

Other settings
^^^^^^^^^^^^^^

.. autodata:: config.settings.common.INSTANCE_SUPPORT_MESSAGE_DELAY
.. autodata:: config.settings.common.FUNKWHALE_SUPPORT_MESSAGE_DELAY
.. autodata:: config.settings.common.MIN_DELAY_BETWEEN_DOWNLOADS_COUNT
.. autodata:: config.settings.common.MARKDOWN_EXTENSIONS
.. autodata:: config.settings.common.LINKIFIER_SUPPORTED_TLDS

User permissions
----------------

Funkwhale's permission model works as follows:

- Anonymous users cannot do anything unless configured specifically
- Logged-in users can use the application, but cannot do things that affect
  the whole instance
- Superusers can do anything

To make things more granular and allow some delegation of responsibility,
superusers can grant specific permissions to specific users. Available
permissions are:

- **Manage instance-level settings**: users with this permission can edit instance
  settings as described in :ref:`instance-settings`
- **Manage library**: users with this permission can import new music in the
  instance
- **Manage library federation**: users with this permission can ask to federate with
  other instances, and accept/deny federation requests from other instances

There is no dedicated interface to manage users permissions, but superusers
can login on the :doc:`Django's admin <django>` at ``/api/admin/`` and grant permissions
to users at ``/api/admin/users/user/``.

Front-end settings
------------------

We offer a basic mechanism to customize the behavior and look and feel of Funkwhale's Web UI.
To use any of the options below, you will need to create a custom JSON configuration file and serve it
on ``https://yourinstanceurl/settings.json``.

On typical deployments, this url returns a 404 error, which is simply ignored.

Set-up
------

First, create the settings file:

.. code-block:: shell

    cd /srv/funkwhale/

    # create a directory for your configuration file
    # you can use a different name / path of course
    mkdir custom

    # populate the configuration file with default values
    cat <<EOF > custom/settings.json
    {
      "additionalStylesheets": [],
      "defaultServerUrl": null
    }
    EOF

Once the ``settings.json`` file is created, you will need to serve it from your reverse proxy.

If you are using nginx, add the following snippet to your vhost configuration::

    location /settings.json {
        alias /srv/funkwhale/custom/settings.json;
    }

On apache, add the following to your vhost configuration::

    Alias /settings.json /srv/funkwhale/custom/settings.json

Then reload your reverse proxy.

At this point, visiting ``https://yourinstanceurl/settings.json`` should serve the content
of the settings.json file.

.. warning::

    The settings.json file must be a valid JSON file. If you have any issue, try linting
    the file with a tool such as `<https://github.com/zaach/jsonlint>`_ to detect potential
    syntax issues.

Available configuration options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Your :file:`settings.json` can contain the following options:

+----------------------------------+--------------------+---------------------------------------+---------------------------------------------------------------+
| Name                             | Type               | Example value                         | Description                                                   |
+----------------------------------+--------------------+---------------------------------------+---------------------------------------------------------------+
| ``additionalStylesheets``        | Array of URLs      | ``["https://test/theme.css"]``        | A list of stylesheets URL (absolute or relative)              |
|                                  |                    | (default: ``[]``)                     | that the web UI should load. see the "Theming" section        |
|                                  |                    |                                       | below for a detailed explanation                              |
|                                  |                    |                                       |                                                               |
+----------------------------------+--------------------+---------------------------------------+---------------------------------------------------------------+
| ``defaultServerUrl``             | URL                | ``"https://api.yourdomain.com"``      | The URL of the API server this front-end should               |
|                                  |                    | (default: ``null``)                   | connect with. If null, the UI will use                        |
|                                  |                    |                                       | the value of VUE_APP_INSTANCE_URL                             |
|                                  |                    |                                       | (specified during build) or fallback to the current domain    |
+----------------------------------+--------------------+---------------------------------------+---------------------------------------------------------------+

Missing options or options with a ``null`` value in the ``settings.json`` file are ignored.

Theming
^^^^^^^

To theme your Funkwhale instance, you need:

1. A CSS file for your theme, that can be loaded by the front-end
2. To update the value of ``additionalStylesheets`` in your settings.json file to point to your CSS file URL

.. code-block:: shell

    cd /srv/funkwhale/custom
    nano settings.json
    # append
    # "additionalStylesheets": ["/front/custom/custom.css"]
    # to the configuration or replace the existing value, if any

    # create a basic theming file changing the background to red
    cat <<EOF > custom.css
    body {
      background-color: red;
    }
    EOF

The last step to make this work is to ensure your CSS file is served by the reverse proxy.

On nginx, add the following snippet to your vhost config::

    location /custom {
        alias /srv/funkwhale/custom;
    }

On apache, use the following::

    Alias /custom /srv/funkwhale/custom

    <Directory "/srv/funkwhale/custom">
      Options FollowSymLinks
      AllowOverride None
      Require all granted
    </Directory>

Once done, reload your reverse proxy, refresh Funkwhale in your web browser, and you should see
a red background.

.. note::

    You can reference external urls as well in ``additionalStylesheets``, simply use
    the full urls. Be especially careful with external urls as they may affect your users
    privacy.

.. warning::

    Loading additional stylesheets and CSS rules can affect the performance and
    usability of your instance. If you encounter issues with the interfaces and use
    custom stylesheets, try to disable those to ensure the issue is not caused
    by your customizations.
