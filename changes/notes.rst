Next release notes
==================

.. note::

    Those release notes refer to the current development branch and are reset
    after each release.


Avoid mixed content when deploying mono-container behind proxy [Manual action required]
---------------------------------------------------------------------------------------------

*You are only concerned if you use the mono-container docker deployment behind a reverse proxy*

Because of `an issue in our mono-container configuration <https://github.com/thetarkus/docker-funkwhale/issues/19>`_, users deploying Funkwhale via docker
using our `funkwhale/all-in-one` image could face some mixed content warnings (and possibly other troubles)
when browsing the Web UI.

This is fixed in this release, but on existing deployments, you'll need to add ``NESTED_PROXY=1`` in your container
environment (either in your ``.env`` file, or via your container management tool), then recreate your funkwhale container.
