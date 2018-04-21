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

    You should restart all funwhale processes when you change the values
    on environment variables.


Instance settings
-----------------

Those settings are stored in database and do not require a restart of your
instance after modification. They typically relate to higher level configuration,
such your instance description, signup policy and so on.

There is no polished interface for those settings, yet, but you can view update
them using the administration interface provided by Django (the framework funkwhale is built on).

The URL should be ``/api/admin/dynamic_preferences/globalpreferencemodel/`` (prepend your domain in front of it, of course).

If you plan to use acoustid and external imports
(e.g. with the youtube backends), you should edit the corresponding
settings in this interface.

Configuration reference
-----------------------

.. _setting-MUSIC_DIRECTORY_PATH:

``MUSIC_DIRECTORY_PATH``
^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``None``

The path on your server where Funwkhale can import files using :ref:`in-place import
<in-place-import>`. It must be readable by the webserver and funkwhale
api and worker processes.

On docker installations, we recommend you use the default of ``/music``
for this value. For non-docker installation, you can use any absolute path.
``/srv/funkwhale/data/music`` is a safe choice if you don't know what to use.

.. note:: This path should not include any trailing slash

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
``/srv/funkwhale/data``. This must be readable by the webserver.

On non-docker setup, you don't need to configure this setting.

.. note:: This path should not include any trailing slash
