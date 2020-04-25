FROM python:3.6

RUN apt-get update && apt-get install -y graphviz
RUN pip install sphinx livereload sphinx_rtd_theme django-environ django
WORKDIR /app/docs
