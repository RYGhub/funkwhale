Systemd configuration
----------------------

Systemd offers a convenient way to manage your funkwhale instance if you're
not using docker.

We'll see how to setup systemd to proprely start a funkwhale instance.

First, download the sample unitfiles:

.. parsed-literal::

    curl -L -o "/etc/systemd/system/funkwhale.target" "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/funkwhale.target"
    curl -L -o "/etc/systemd/system/funkwhale-server.service" "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/funkwhale-server.service"
    curl -L -o "/etc/systemd/system/funkwhale-worker.service" "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/funkwhale-worker.service"
    curl -L -o "/etc/systemd/system/funkwhale-beat.service" "https://code.eliotberriot.com/funkwhale/funkwhale/raw/|version|/deploy/funkwhale-beat.service"

This will download three unitfiles:

- ``funkwhale-server.service`` to launch the funkwhale web server
- ``funkwhale-worker.service`` to launch the funkwhale task worker
- ``funkwhale-beat.service`` to launch the funkwhale task beat (this is for recurring tasks)
- ``funkwhale.target`` to easily stop and start all of the services at once

You can of course review and edit them to suit your deployment scenario
if needed, but the defaults should be fine.

Once the files are downloaded, reload systemd:

.. code-block:: shell

    systemctl daemon-reload

And start the services:

.. code-block:: shell

    systemctl start funkwhale.target

You can check the statuses of all processes like this:

.. code-block:: shell

    systemctl status funkwhale-\*
