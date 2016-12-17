FROM python:3

MAINTAINER Jelle Besseling <jelle@pingiun.com>

COPY . /app

WORKDIR /app

RUN curl http://uwsgi.it/install | bash -s default /tmp/uwsgi && mkdir /tmp/socket && pip install -r requirements.txt 

ENV UWSGI_MOUNTPOINT /

CMD /tmp/uwsgi -s /tmp/socket/uwsgi.sock --manage-script-name --mount $UWSGI_MOUNTPOINT=urlshorten:app
