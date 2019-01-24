FROM alpine:3.8

RUN \
    echo 'installing dependencies' && \
    apk add                \
    bash             \
    git             \
    gettext            \
    musl-dev           \
    gcc \
    postgresql-dev \
    python3-dev        \
    py3-psycopg2       \
    py3-pillow         \
    libldap            \
    ffmpeg             \
    libpq              \
    libmagic           \
    libffi-dev         \
    zlib-dev           \
    openldap-dev && \
    \
    \
    ln -s /usr/bin/python3 /usr/bin/python

RUN mkdir /requirements
COPY ./requirements/base.txt /requirements/base.txt
# hack around https://github.com/pypa/pip/issues/6158#issuecomment-456619072
ENV PIP_DOWNLOAD_CACHE=/noop/
RUN \
    echo 'fixing requirements file for alpine' && \
    sed -i '/Pillow/d' /requirements/base.txt && \
    \
    \
    echo 'installing pip requirements' && \
    pip3 install --upgrade pip && \
    pip3 install setuptools wheel && \
    pip3 install -r /requirements/base.txt && \
    rm -rf $PIP_DOWNLOAD_CACHE

ARG install_dev_deps=0
COPY ./requirements/*.txt /requirements/
RUN \
    if [ "$install_dev_deps" = "1" ] ; then echo "Installing dev dependencies" && pip3 install --no-cache-dir -r /requirements/local.txt -r /requirements/test.txt ; else echo "Skipping dev deps installation" ; fi

ENTRYPOINT ["./compose/django/entrypoint.sh"]
CMD ["./compose/django/daphne.sh"]

COPY . /app
WORKDIR /app
