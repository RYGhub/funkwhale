FROM python:3.5

ENV PYTHONUNBUFFERED 1

# Requirements have to be pulled and installed here, otherwise caching won't work

COPY ./requirements.apt /requirements.apt
RUN apt-get update -qq && grep "^[^#;]" requirements.apt | xargs apt-get install -y
RUN curl -L https://github.com/acoustid/chromaprint/releases/download/v1.4.2/chromaprint-fpcalc-1.4.2-linux-x86_64.tar.gz | tar -xz -C /usr/local/bin --strip 1
COPY ./requirements/base.txt /requirements/base.txt
RUN pip install -r /requirements/base.txt
COPY ./requirements/production.txt /requirements/production.txt
RUN pip install -r /requirements/production.txt

COPY . /app

# Since youtube-dl code is updated fairly often, we split it here
RUN pip install --upgrade youtube-dl

WORKDIR /app

ENTRYPOINT ["./compose/django/entrypoint.sh"]
