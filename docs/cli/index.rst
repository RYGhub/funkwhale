Funkwhale CLI
=============

`Funkwhale CLI <https://dev.funkwhale.audio/funkwhale/cli/>`_ is a command-line interface you can install on your local computer
to interact with any Funkwhale server via the REST API. It's especially useful if you need to do repetitive operations
or write scripts that interact with Funkwhale servers.

Here is a (non-exhaustive) list of operations you can perform via the CLI:

- Manage libraries
- Upload local files
- Retrieve and search tracks, albums and artists
- Download tracks
- Manage playlists
- Manage favorites

.. contents:: Table of Contents



Installation
------------

We provide a prebuilt binary for Linux::

    curl -L "https://dev.funkwhale.audio/funkwhale/cli/-/jobs/artifacts/master/raw/funkwhale?job=build-linux" -o /usr/local/bin/funkwhale
    chmod +x /usr/local/bin/funkwhale

You can also install from source with::

    pip3 install --user git+https://dev.funkwhale.audio/funkwhale/cli
    # the executable will be available at ~/.local/bin/funkwhale

.. note::

    Installing from source requires you have Python 3.6 or higher available.

You can check the installation was successful by running ``funkwhale --help``. This should output
the list of available commands and the CLI description.

Basic usage
-----------

Here are a couple of commands you can try to get started:

.. code-block:: shell

    # Display public server info of demo.funkwhale.audio
    funkwhale -H https://demo.funkwhale.audio server info

    # List tracks from open.audio
    funkwhale -H https://open.audio tracks ls

    # Search artists matching "zebra" on open.audio
    funkwhale -H https://open.audio artists ls "zebra"

More examples
-------------

You should find enough in this reference document to start using the CLI on your own.

However, we've compiled :doc:`a list of example uses of the CLI <examples>` with advice and explanations, if you want to check it out ;)

Getting help
------------

The most basic way to get help is to run ``funkwhale --help``. It will list available commands, namespaces and arguments that are common to all commands.

You can also append the ``--help`` flag after any command to get more information about its arguments and options, like this: ``funkwhale albums ls --help``

The CLI offers nested commands. For instance, ``funkwhale albums`` isn't a valid command in itself, but a namespace for all albums-related commands.

To get the help of a specific namespace and list all its available commands, simply run ``funkwhale <namespace> --help``.

Authentication
--------------

The CLI uses JWT tokens to interact with the API. You can either:

1. Run ``funkwhale login``, which will ask you your Funkwhale username and password and store a JWT token in your local keyring. This token will be used automatically afterwards.
2. Explicitly pass a token to the command via the ``-t`` flag or the ``FUNKWHALE_TOKEN`` environment variable

If you use ``funkwhale login``, you can delete the local token with ``funkwhale logout``.

You can check that you are fully authenticated by running ``funkwhale users me``. It will display information relating to your user profile.

Configuration
-------------

To work, the CLI needs to be pointed to a Funkwhale server. This can be done in various ways:

- Via the ``-H https://funkwhale.domain`` flag when calling the CLI
- Via the ``FUNKWHALE_SERVER_URL`` environment variable
- Via an env file (see below)

Env file
^^^^^^^^

The CLI will try to read configuration options from a ``.env`` file in the current directory, or from ``~/.config/funkwhale/env``.

You can also give it a path to another env file via the ``-e /path/to/.envfile`` flag or the ``ENV_FILE`` environment variable.

An env file simply contains a list of variables, using the same syntax as environment variables (comments starting with # are allowed). Example::

    # ~/Music/.env
    FUNKWHALE_SERVER_URL=https://my.funkwhale.server


List of configuration options
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+
| CLI Flag                             | Environment variable                           | Example value                              | Description                                                   |
+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+
| ``-e``, ``--env-file``               | ``ENV_FILE``                                   | ``~/Music/.env``                           | Path to a local env file to use for configuration             |
+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+
| ``-H``, ``--url``                    | ``FUNKWHALE_SERVER_URL``                       | ``https://demo.funkwhale.audio``           | The URL of the Funkwhale server the CLI should contact        |
+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+
| ``-t``, ``--token``                  | ``FUNKWHALE_TOKEN``                            | ``eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI``        | A JWT token to use for authentication                         |
+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+
| ``--no-login``                       | ``FUNKWHALE_NO_LOGIN``                         | ``true``                                   | Completely disable authentication and keyring                 |
+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+
| ``-v``, ``--verbosity``              |                                                | One of ``CRITICAL``, ``ERROR``,            | Control the verbosity (default is INFO)                       |
|                                      |                                                | ``WARNING``, ``INFO`` or ``DEBUG``         |                                                               |
+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+
| ``-q``, ``--quiet``                  | ``FUNKWHALE_QUIET``                            | ``true``                                   | Completely disable logging                                    |
+--------------------------------------+------------------------------------------------+--------------------------------------------+---------------------------------------------------------------+

Listing results
---------------

All commands that list results - such as ``funkwhale albums ls`` or ``funkwhale tracks ls`` - share similar behaviors and sets of arguments.

Filtering
^^^^^^^^^

Results can be filtered using the ``-f`` or ``--filter`` flag. Provided values are transmitted directly in the querystring when the requests to the API is made::

    # retrieve playable tracks
    funkwhale tracks ls -f "playable=true"

The flag can be provided multiple times, to add multiple filter conditions::

    # retrieve playable tracks with a CC-BY-SA 4.0 license
    funkwhale tracks ls -f "playable=true" -f "license=cc-by-sa-4.0"

.. note::

    The list of supported fields for filtering depends on the resource being queried, and can be found in our `API documentation`_.


Searching
^^^^^^^^^

Any text provided after the ``ls`` command will be considered a search query and transmitted to the API::

    # retrieve tracks matching the search query "Electro Swing"
    funkwhale tracks ls Electro Swing

.. note::

    This is technically equivalent to filtering with a ``q`` parameter as described above::

        funkwhale tracks ls -f "q=Electro Swing"


Ordering
^^^^^^^^

You can control the ordering of the results with the `-o` or ``--ordering`` flag::

    # retrieve albums by creation date, in ascending order
    funkwhale albums ls -o creation_date

.. note::

    Ordering in descending order is supported by prefixing the field name with ``-``, e.g: ``-o -creation_date``

.. note::

    The list of supported fields for ordering depends on the resource being queried, and can be found in our `API documentation`_.


Pagination
^^^^^^^^^^

You can retrieve a specific result page using the ``-p`` or ``--page`` flag::

    # retrieve the second page of albums
    funkwhale albums ls -p 2

You can also alter the size of the pages using the ``-s`` or ``--page-size`` flag::

    # retrieve five albums
    funkwhale albums ls -s 5

Sometimes, you may want to retrieve multiple pages of results at once. This is supported using the ``-l`` or ``--limit`` flag::

    # retrieve the first 3 pages of albums
    funkwhale albums ls -l 3

You can, of course, combine these flags::

    # retrieve 3 pages of 12 albums, starting on the 4th page
    funkwhale albums ls --limit 3 --page-size 12 --page 4

Output
^^^^^^

While the default output displays a human-readable table, you can customize it.

The ``--raw`` flag will simply output the raw JSON payload returned by the API server::

    funkwhale artists ls --raw

The ``-h`` or ``--no-headers`` flag simply removes the table column headers.

The ``-t`` or ``--format`` flag alters the rendering of result, depending on the provided value::

    # list artists outputting a html table
    funkwhale artists ls -t html
    # output a github/markdown table
    funkwhale artists ls -t github

Available formats are: ``fancy_grid``, ``github``, ``grid``, ``html``, ``jira``, ``latex``, ``latex_booktabs``, ``latex_raw``, ``mediawiki``, ``moinmoin``, ``orgtbl``, ``pipe``, ``plain``, ``presto``, ``psql``, ``rst``, ``simple``, ``textile``, ``tsv``, ``youtrack``

The ``-c`` or ``--column`` flag gives you control on the displayed columns::

    # list artists, displaying only artist ID and number of tracks
    funkwhale artists ls -c ID -c Tracks

For a given resource, the list of available columns can be found by running ``funkwhale <resource> ls --help``.

The ``-i`` or ``--ids`` flag displays only the IDs of results, one per line::

    funkwhale artists ls --ids

This is especially useful in conjunction with other commands (like deletion commands) and piping.
Note that this is also technically equivalent to applying the ``--no-headers``, ``--format plain`` and ``--column ID`` flags.

Deleting objects
----------------

Some resources support deletion, via commands such as ``funkwhale libraries rm`` or ``funkwhale playlists rm``, followed by one or more IDs::

    # delete playlists 42 and 23
    funkwhale playlists rm 42 23

By default, the ``rm`` command will ask for confirmation, but you can disable this behavior by providing the ``--no-input`` flag.


.. _API Documentation: https://docs.funkwhale.audio/swagger/
