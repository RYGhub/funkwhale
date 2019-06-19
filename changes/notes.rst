Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.


Replaced Daphne by Gunicorn/Uvicorn [manual action required, non-docker only]
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To improve the performance, stability and reliability of Funkwhale's web processes,
we now recommend using Gunicorn and Uvicorn instead of Daphne. This combination unlock new use cases such as:

- zero-downtime upgrades
- configurable number of web worker processes

Based on our benchmarks, Gunicorn/Unicorn is also faster and more stable under higher workloads compared to Daphne.

To benefit from this enhancement on existing instances, you need to add ``FUNKWHALE_WEB_WORKERS=1`` in your ``.env`` file
(use a higher number if you want to have more web worker processes).

Then, edit your ``/etc/systemd/system/funkwhale-server.service`` and replace the ``ExecStart=`` line with
``ExecStart=/srv/funkwhale/virtualenv/bin/gunicorn config.asgi:application -w ${FUNKWHALE_WEB_WORKERS} -k uvicorn.workers.UvicornWorker -b ${FUNKWHALE_API_IP}:${FUNKWHALE_API_PORT}``

Then reload the configuration change with ``sudo systemctl daemon-reload`` and ``sudo systemctl restart funkwhale-server``.
