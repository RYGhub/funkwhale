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
