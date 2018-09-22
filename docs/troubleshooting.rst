Troubleshooting
===============

Various errors and issues can arise on your Funkwhale instance, caused by configuration errors,
deployment/environment specific issues, or bugs in the software itself.

On this document, you'll find:

- Tools and commands you can use to better understand the issues
- A list of common pitfalls and errors and how to solve them
- A collection of links and advice to get help from the community and report new issues

Diagnose problems
^^^^^^^^^^^^^^^^^

Funkwhale is made of several components, each one being a potential cause for failure. Having an even basic overview
of Funkwhale's technical architecture can help you understand what is going on. You can refer to :doc:`the technical architecture </architecture>` for that.

Problems usually fall into one of those categories:

- **Frontend**: Funkwhale's interface is not loading, not behaving as expected, music is not playing
- **API**: the interface do not display any data or show errors
- **Import**: uploaded/imported tracks are not imported correctly or at all
- **Federation**: you cannot contact other Funkwhale servers, access their library, play federated tracks
- **Everything else**

Each category comes with its own set of diagnose tools and/or commands we will detail below. We'll also give you simple
steps for each type of problem. Please try those to see if it fix your issues. If none of those works, please report your issue on our
issue tracker.

Frontend issues
^^^^^^^^^^^^^^^

Diagnostic tools:

- Javascript and network logs from your browser console (see instructions on how to open it in `Chrome <https://developers.google.com/web/tools/chrome-devtools/console/>`_ and  `Firefox <https://developer.mozilla.org/en-US/docs/Tools/Web_Console/Opening_the_Web_Console>`_
- Proxy and API access and error logs (see :ref:`access-logs`)
- The same operation works from a different browser

Common problems
***************

The front-end is completely blank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You are visiting Funkwhale, but you don't see anything.

- Try from a different browser
- Check network errors in your browser console. If you see responses with 40X or 50X statuses, there is probably an issue with the webserver configuration
- If you don't see anything wrong in the network console, check the Javascript console
- Disable your browser extensions (like adblockers)

Music is not playing
~~~~~~~~~~~~~~~~~~~~

You have some tracks in your queue that don't play, or the queue is jumping from one track to the next until
there is no more track available:

- Try with other tracks. If it works with some tracks but not other tracks, this may means that the failing tracks are not probably imported
  or that your browser does not support a specific audio format
- Check the network and javascript console for potential errors

Tracks are not appending to the queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When clicking on "Play", "Play all albums" or "Play all" buttons, some tracks are not appended to the queue. This is
actually a feature of Funkwhale: those tracks have no file associated with them, so we cannot play them.

Specific pages are loading forever or blank
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When viewing a given page, the page load never ends (you continue to see the spinner), or nothing seems to appear at all:

- Ensure your internet connection is up and running
- Ensure your instance is up and running
- Check the network and javascript console for potential errors


Backend issues
^^^^^^^^^^^^^^

Diagnostic tools:

- Reverse proxy logs:
    - Apache logs should be available at :file:`/var/log/apache/access.log` and :file:`/var/log/apache/error.log`
    - Nginx logs should be available at :file:`/var/log/nginx/access.log` and :file:`/var/log/nginx/error.log`
- API logs:
    - Docker setup: ``docker-compose logs -f --tail=50 api`` (remove the ``--tail`` flag to get the full logs)
    - Non-docker setup: ``journalctl -xn -u funkwhale-server``

.. note::

    If you edit your .env file to test a new configuration, you have to restart your services to pick up the changes:

    - Docker setup: ``docker-compose up -d``
    - Non-docker setup: ``systemctl restart funkwhale.target``

Common problems
***************

Instance work properly, but audio files are not served (404 error)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- If you're using docker, ensure the ``MEDIA_ROOT`` variable is commented in your env file
- Ensure the ``_protected/media`` block points toward the path where media files are stored (``/srv/funkwhale/data/media``, by default)
- If you're using in-place import, ensure :ref:`setting-MUSIC_DIRECTORY_PATH`, :ref:`setting-MUSIC_DIRECTORY_SERVE_PATH` and :ref:`setting-REVERSE_PROXY_TYPE` are configured properly, and that the files are readable by the webserver

Weakref error when running ``python manage.py <command>``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

On Python <3.6, you may see this kind of errors when running commands like ``python manage.py migrate``::

    Exception ignored in: <function WeakValueDictionary.__init__.<locals>.remove at 0x107e7a6a8>
    Traceback (most recent call last):
    File "/srv/funkwhale/venv/lib/python3.5/weakref.py", line 117, in remove
    TypeError: 'NoneType' object is not callable

This is caused by a bug in Python (cf https://github.com/celery/celery/issues/3818), and is not affecting in any way
the command you execute. You can safely ignore this error.

``Your models have changes that are not yet reflected in a migration`` warning
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When running ``python manage.py migrate`` (both in docker or non-docker), you may end-up with this::

    Operations to perform:
    Apply all migrations: account, admin, auth, authtoken, common, contenttypes, dynamic_preferences, favorites, federation, history, music, playlists, radios, requests, sessions, sites, socialaccount, taggit, users
    Running migrations:
    No migrations to apply.

    Your models have changes that are not yet reflected in a migration, and so won't be applied.
    Run 'manage.py makemigrations' to make new migrations, and then re-run 'manage.py migrate' to apply them.

This warning can be safely ignored. You should not run the suggested ``manage.py makemigrations`` command.

File import issues
^^^^^^^^^^^^^^^^^^

Unless you are using the CLI to import files, imports are send as tasks in a queue to a celery worker that will process them.

Diagnostic tools:

- Celery worker logs:
    - Docker setup: ``docker-compose logs -f --tail=50 celeryworker`` (remove the ``--tail`` flag to get the full logs)
    - Non-docker setup: ``journalctl -xn -u funkwhale-worker``

Federation issues
^^^^^^^^^^^^^^^^^

Received federations messages are sent to a dedicated task queue and processed asynchronously by a celery worker.

Diagnostic tools:

- API logs:
    - Docker setup: ``docker-compose logs -f --tail=50 api`` (remove the ``--tail`` flag to get the full logs)
    - Non-docker setup: ``journalctl -xn -u funkwhale-server``
- Celery worker logs:
    - Docker setup: ``docker-compose logs -f --tail=50 celeryworker`` (remove the ``--tail`` flag to get the full logs)
    - Non-docker setup: ``journalctl -xn -u funkwhale-worker``

Common problems
***************

I have no access to another instance library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Check if it works with the demo library (library@demo.funkwhale.audio)
- Check if the remote library received your follow request and approved it
- Trigger a scan via the interface
- Have a look in the celery logs for potential errors during the scan

Other problems
^^^^^^^^^^^^^^

It's a bit hard to give targeted advice about problems that do not fit in the previous categories. However, we can recommend to:

- Try to identify the scope of the issue and reproduce it reliably
- Ensure your instance is configured as detailed in the installation documentation, and if you did not use the default
  values, to check what you changed
- To read the .env file carefuly, as most of the options are described in the comments


Report an issue or get help
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Well be more than happy to help you to debug installation and configuration issues. The main channel
for receiving support about your Funkwhale installation is the `#funkwhale-troubleshooting:matrix.org <https://riot.im/app/#/room/#funkwhale-troubleshooting:matrix.org>`_ Matrix channel.

Before asking for help, we'd really appreciate if you took the time to go through this document and try to diagnose the problem yourself. But if you don't find
anything relevant or don't have the time, we'll be there for you!

Here are a few recommendations on how to structure and what to include in your help requests:

- Give us as much context as possible about your installation (OS, version, Docker/non-docker, reverse-proxy type, relevant logs and errors, etc.)
- Including screenshots or small gifs or videos can help us considerably when debugging front-end issues

You can also open issues on our `issue tracker <https://code.eliotberriot.com/funkwhale/funkwhale/issues>`_. Please have a quick look for
similar issues before doing that, and use the issue tracker only to report bugs, suggest enhancements (both in the software and the documentation) or new features.

.. warning::

    If you ever need to share screenshots or urls with someone else, ensure those do not include your personnal token.
    This token is binded to your account and can be used to connect and use your account.

    Urls that includes your token looks like: ``https://your.instance/api/v1/uploads/42/serve/?jwt=yoursecrettoken``

Improving this documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you feel like something should be improved in this document (and in the documentation in general), feel free to `edit
it <https://code.eliotberriot.com/funkwhale/funkwhale/tree/develop/docs>`_ and open a Merge Request. If you lack time or skills
to do that, you can open an issue to discuss that, and someone else will do it.
