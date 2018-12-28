Optimizing your Funkwhale instance
==================================

Depending on your requirements, you may want to reduce as much as possible
Funkwhale's memory footprint.

Reduce workers concurrency
--------------------------

Asynchronous tasks are handled by a celery worker, which will by default
spawn a worker process per CPU available. This can lead to a higher
memory usage.

You can control this behavior using the ``--concurrency`` flag.
For instance, setting ``--concurrency=1`` will spawn only one worker.

This flag should be appended after the ``celery -A funkwhale_api.taskapp
worker`` command in your :file:`docker-compose.yml` file if your using Docker,
or in your :file:`/etc/systemd/system/funkwhale-worker.service` otherwise.

.. note::

    Reducing concurrency comes at a cost: asynchronous tasks will be processed
    more slowly. However, on small instances, this should not be an issue.


Switch from prefork to solo pool
--------------------------------

Using a different pool implementation for Celery tasks may also help.

Using the ``solo`` pool type should reduce your memory consumption.
You can control this behavior using the ``--pool=solo`` flag.

This flag should be appended after the ``celery -A funkwhale_api.taskapp worker``
command in your :file:`docker-compose.yml` file if you're using Docker, or in
your :file:`/etc/systemd/system/funkwhale-worker.service` otherwise.
