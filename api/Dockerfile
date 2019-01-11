FROM python:3.6

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work
RUN echo 'deb http://httpredir.debian.org/debian/ jessie-backports main' > /etc/apt/sources.list.d/ffmpeg.list
COPY ./requirements.apt /requirements.apt
RUN apt-get update; \
    grep "^[^#;]" requirements.apt | \
    grep -Fv "python3-dev" | \
    xargs apt-get install -y --no-install-recommends; \
    rm -rf /usr/share/doc/* /usr/share/locale/*

COPY ./requirements/base.txt /requirements/base.txt
RUN pip install -r /requirements/base.txt

COPY . /app

# Since youtube-dl code is updated fairly often, we split it here
RUN pip install --upgrade youtube-dl

WORKDIR /app

ENTRYPOINT ["./compose/django/entrypoint.sh"]
CMD ["./compose/django/daphne.sh"]
