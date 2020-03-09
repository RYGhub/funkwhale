FROM alpine:3.10 as builder

RUN \
    echo 'installing dependencies' && \
    apk add --no-cache               \
    git             \
    musl-dev           \
    gcc \
    postgresql-dev \
    python3-dev        \
    py3-psycopg2       \
    libldap            \
    libffi-dev         \
    make         \
    zlib-dev           \
    jpeg-dev           \
    openldap-dev \
    && \
    \
    ln -s /usr/bin/python3 /usr/bin/python

# create virtual env for next stage
RUN python -m venv /venv
# emulate activation by prefixing PATH
ENV PATH="/venv/bin:$PATH" VIRTUAL_ENV=/venv

RUN mkdir /requirements
COPY ./requirements/base.txt /requirements/base.txt
# hack around https://github.com/pypa/pip/issues/6158#issuecomment-456619072
ENV PIP_DOWNLOAD_CACHE=/noop/
RUN \
    echo 'installing pip requirements' && \
    pip3 install --upgrade pip && \
    pip3 install setuptools wheel && \
    pip3 install -r /requirements/base.txt && \
    rm -rf $PIP_DOWNLOAD_CACHE

ARG install_dev_deps=0
COPY ./requirements/*.txt /requirements/
RUN \
    if [ "$install_dev_deps" = "1" ] ; then echo "Installing dev dependencies" && pip3 install --no-cache-dir -r /requirements/local.txt -r /requirements/test.txt ; else echo "Skipping dev deps installation" ; fi


FROM alpine:3.10 as build-image

COPY --from=builder /venv /venv
# emulate activation by prefixing PATH
ENV PATH="/venv/bin:$PATH"

RUN apk add --no-cache \
    libmagic \
    bash             \
    gettext            \
    python3        \
    jpeg-dev \
    ffmpeg             \
    libpq              \
    && \
    \
    ln -s /usr/bin/python3 /usr/bin/python


ENTRYPOINT ["./compose/django/entrypoint.sh"]
CMD ["./compose/django/server.sh"]

COPY . /app
WORKDIR /app
