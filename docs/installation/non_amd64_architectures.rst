Running Funkwhale on non amd64 architectures
============================================

Funkwhale should be runnable on any architecture assuming Funkwhale installation dependencies are satisfied.

On non-docker deployments (e.g. when deploying on debian), this should be completely transparent.

On docker deployments, you will need to build Funkwhale's image yourself, because we don't provide
pre-built multi-arch images on the Docker Hub yet. The build process itself only requires git,
Docker and is described below.

Building the mono-process Docker image (funkwhale/funkwhale)
-------------------------------------------------------------

This image is intended to be used in conjunction with our :ref:`Multi-container installation guide <docker-multi-container>`.
guide.

.. parsed-literal::

    export FUNKWHALE_VERSION="|version|"

.. note::

    Replace by develop for building a development branch image.

.. code-block:: shell

    cd /tmp
    git clone https://dev.funkwhale.audio/funkwhale/funkwhale.git
    cd funkwhale
    git checkout $FUNKWHALE_VERSION
    cd api

    # download the pre-built front-end files
    frontend_artifacts="https://dev.funkwhale.audio/funkwhale/funkwhale/-/jobs/artifacts/$FUNKWHALE_VERSION/download?job=build_front"
    curl -L -o front.zip $frontend_artifacts
    unzip front.zip
    cp -r front/dist frontend

    docker build -t funkwhale/funkwhale:$FUNKWHALE_VERSION .



Building the mono-container Docker image (funkwhale/all-in-one)
--------------------------------------------------------------

This image is intended to be used in conjunction with our :ref:`Mono-container installation guide <docker-mono-container>`.
guide.


.. parsed-literal::

    export FUNKWHALE_VERSION="|version|"

.. note::

    Replace by develop for building a development branch image.

.. code-block:: shell

    cd /tmp
    git clone https://github.com/thetarkus/docker-funkwhale.git
    cd docker-funkwhale

    # download the pre-built front-end files
    # download Funkwhale front and api artifacts and nginx configuration
    ./scripts/download-artifact.sh src/ $FUNKWHALE_VERSION build_front
    ./scripts/download-artifact.sh src/ $FUNKWHALE_VERSION build_api
    ./scripts/download-nginx-template.sh src/ $FUNKWHALE_VERSION

    docker build --build-arg=arch=$(uname -m) -t funkwhale/all-in-one:$FUNKWHALE_VERSION .
