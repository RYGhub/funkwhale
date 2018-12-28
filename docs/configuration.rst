Instance configuration
======================

General configuration is achieved using two type of settings.

Environment variables
---------------------

Those are located in your ``.env`` file, which you should have created
during installation.

Options from this file are heavily commented, and usually target lower level
and technical aspects of your instance, such as database credentials.

.. note::

    You should restart all funkwhale processes when you change the values
    on environment variables.


.. _instance-settings:

Instance settings
-----------------

Those settings are stored in database and do not require a restart of your
instance after modification. They typically relate to higher level configuration,
such your instance description, signup policy and so on.

You can edit those settings directly from the web application, assuming
you have the required permissions. The URL is ``/manage/settings``, and
you will also find a link to this page in the sidebar.

If you plan to use acoustid and external imports
(e.g. with the youtube backends), you should edit the corresponding
settings in this interface.

.. note::

    If you have any issue with the web application, a management interface is also
    available for those settings from Django's administration interface. It's
    less user friendly, though, and we recommend you use the web app interface
    whenever possible.

    The URL should be ``/api/admin/dynamic_preferences/globalpreferencemodel/`` (prepend your domain in front of it, of course).


Configuration reference
-----------------------

.. _setting-EMAIL_CONFIG:

``EMAIL_CONFIG``
^^^^^^^^^^^^^^^^

Determine how emails are sent.

Default: ``consolemail://``

Possible values:

- ``consolemail://``: Output sent emails to stdout
- ``dummymail://``: Completely discard sent emails
- ``smtp://user:password@youremail.host:25``: Send emails via SMTP via youremail.host on port 25, without encryption, authenticating as user "user" with password "password"
- ``smtp+ssl://user:password@youremail.host:465``: Send emails via SMTP via youremail.host on port 465, using SSL encryption, authenticating as user "user" with password "password"
- ``smtp+tls://user:password@youremail.host:587``: Send emails via SMTP via youremail.host on port 587, using TLS encryption, authenticating as user "user" with password "password"

.. _setting-DEFAULT_FROM_EMAIL:

``DEFAULT_FROM_EMAIL``
^^^^^^^^^^^^^^^^^^^^^^

The email address to use to send email.

Default: ``Funkwhale <noreply@yourdomain>``

.. note::

    Both the forms ``Funkwhale <noreply@yourdomain>`` and
    ``noreply@yourdomain`` work.


.. _setting-MUSIC_DIRECTORY_PATH:

``MUSIC_DIRECTORY_PATH``
^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

The path on your server where Funkwhale can import files using :ref:`in-place import
<in-place-import>`. It must be readable by the webserver and Funkwhale
api and worker processes.

On docker installations, we recommend you use the default of ``/music``
for this value. For non-docker installation, you can use any absolute path.
``/srv/funkwhale/data/music`` is a safe choice if you don't know what to use.

.. note:: This path should not include any trailing slash

.. warning::

   You need to adapt your :ref:`reverse-proxy configuration<reverse-proxy-setup>` to
   serve the directory pointed by ``MUSIC_DIRECTORY_PATH`` on
   ``/_protected/music`` URL.

.. _setting-MUSIC_DIRECTORY_SERVE_PATH:

``MUSIC_DIRECTORY_SERVE_PATH``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: :ref:`setting-MUSIC_DIRECTORY_PATH`

When using Docker, the value of :ref:`MUSIC_DIRECTORY_PATH` in your containers
may differ from the real path on your host. Assuming you have the following directive
in your :file:`docker-compose.yml` file::

    volumes:
      - /srv/funkwhale/data/music:/music:ro

Then, the value of :ref:`setting-MUSIC_DIRECTORY_SERVE_PATH` should be
``/srv/funkwhale/data/music``. This must be readable by the webserver.

On non-docker setup, you don't need to configure this setting.

.. note:: This path should not include any trailing slash

.. _setting-REVERSE_PROXY_TYPE:

``REVERSE_PROXY_TYPE``
^^^^^^^^^^^^^^^^^^^^^^

Default: ``nginx``

The type of reverse-proxy behind which Funkwhale is served. Either ``apache2``
or ``nginx``. This is only used if you are using in-place import.

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
can login on the Django's admin at ``/api/admin/`` and grant permissions
to users at ``/api/admin/users/user/``.

Theming
-------

Funkwhale supports custom themes, which are great if you want to personalize the
look and feel of your instance. Theming is achieved by declaring
additional stylesheets you want to load in the front-end.

Customize the settings
^^^^^^^^^^^^^^^^^^^^^^

In order to know what stylesheets to load, the front-end requests the following
url: ``https://your.instance/settings.json``. On typical deployments, this url
returns a 404 error, which is simply ignored.

However, if you return the appropriate payload on this url, you can make the magic
work. We will store the necessary files in the ``/srv/funkwhale/custom`` directory:

.. code-block:: shell

    cd /srv/funkwhale/
    mkdir custom
    cat <<EOF > custom/settings.json
    {
      "additionalStylesheets": ["/custom/custom.css"]
    }
    EOF
    cat <<EOF > custom/custom.css
    body {
      background-color: red;
    }
    EOF

By executing the previous commands, you will end up with two files in your ``/srv/funkwhale/custom``
directory:

- ``settings.json`` will tell the front-end what stylesheets you want to load (``/custom/custom.css`` in this example)
- ``custom.css`` will hold your custom CSS

The last step to make this work is to ensure both files are served by the reverse proxy.

On nginx, add the following snippet to your vhost config::

    location /settings.json {
        alias /srv/funkwhale/custom/settings.json;
    }
    location /custom {
        alias /srv/funkwhale/custom;
    }

On apache, use the following one::

    Alias /settings.json /srv/funkwhale/custom/settings.json
    Alias /custom /srv/funkwhale/custom

    <Directory "/srv/funkwhale/custom">
      Options FollowSymLinks
      AllowOverride None
      Require all granted
    </Directory>

Once done, reload your reverse proxy, refresh Funkwhale in your web browser, and you should see
a red background.

.. note::

    You can reference external urls as well in ``settings.json``, simply use
    the full urls. Be especially careful with external urls as they may affect your users
    privacy.

.. warning::

    Loading additional stylesheets and CSS rules can affect the performance and
    usability of your instance. If you encounter issues with the interfaces and use
    custom stylesheets, try to disable those to ensure the issue is not caused
    by your customizations.
