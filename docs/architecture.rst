Architecture
============

Funkwhale is made of several components, each of them fulfilling a specific mission:

.. graphviz::

    digraph {
        node [shape=record];
        rankdir=TB
        concentrate=true
        user [group="frontend" label="User" fontsize="9"]
        webui [group="frontend" label="Web interface (VueJS SPA)" fontsize="9"]
        subapps [group="frontend" label="Subsonic-compatible apps (DSub, Clementine)" fontsize="9"]
        proxy [label="Reverse proxy (Nginx/Apache)" fontsize="9"]
        api [label="API Server (Django)" fontsize="9"]
        db [label="Database (PostgreSQL)" fontsize="9"]
        cache [label="Cache and message queue (Redis)" fontsize="9"]
        worker [label="Worker (Celery)" fontsize="9"]
        scheduler [label="Task scheduler (Celery Beat)" fontsize="9"]

        user -> subapps -> proxy
        user -> webui -> proxy
        cache -> worker
        proxy -> api
        api -> cache
        api -> db
        scheduler -> cache
        worker -> cache
        worker -> db
    }

This graph may looks a bit scary, so we'll detail the role of each component below.

The user
--------

Funkwhale users can interact with your instance using:

- The official web interface
- Third-party apps

The web interface
-----------------

This refers to Funkwhale's built-in web interface, which is a Single Page application
written in Vue JS. This application will interact with Funkwhale's API to retrieve
or persist data.

Third-party apps
----------------

Since Funkwhale implements a subset of the Subsonic API, it's compatible with existing apps such
as DSub, Ultrasonic or Clementine that support this API. Those apps can be used as a replacement
or in conjunction of the web interface, but the underlying data is the same.

The reverse proxy
-----------------

Funkwhale's API server should never be exposed directly to the internet, as we require
a reverse proxy (Apache or Nginx) for performance and security reasons. The reverse proxy
will receive client HTTP requests, and:

- Proxy them to the API server
- Serve requested static files (Audio files, stylesheets, javascript, fonts...)

The API server
--------------

Funkwhale's API server is the central piece of the project. This component is responsible
for answering and processing user requests, manipulate data from the database, send long-running
tasks to workers, etc.

It's a Python/Django application.

The database
------------

Most of the data such as user accounts, favorites, music metadata or playlist is stored
in a PostgreSQL database.

The cache/message queue
-----------------------

Fetching data from the database is sometimes slow or resource hungry. To reduce
the load, Redis act as a cache for data that is considerably faster than a database.

It is also a message queue that will deliver tasks to the worker.

The worker
----------

Some operations are too long to live in the HTTP request/response cycle. Typically,
importing a bunch of uploaded tracks could take a minute or two.

To keep the API response time as fast as possible, we offload long-running tasks
to a background process, also known as the Celery worker.

Typical tasks include:

- Handling music imports
- Handling federation/ActivityPub messages
- Scanning other instances libraries

This worker is also able to retry failed tasks, or spawn automatically
more process when the number of received tasks increase.

The scheduler
-------------

Some long-running tasks are not triggered by user or external input, but on a recurring
basis instead. The scheduler is responsible for triggering those tasks and put the corresponding
messages in the message queue so the worker can process them.

Recurring tasks include:

- Cache cleaning
- Music metadata refreshing
