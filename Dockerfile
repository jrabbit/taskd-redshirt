FROM debian:stretch

LABEL maintainer "jack@getpizza.cat"

RUN mkdir -p /usr/src/redshirt

COPY Pipfile Pipfile.lock /usr/src/redshirt/

WORKDIR /usr/src/redshirt

RUN apt-get update && apt-get install -y curl python2.7-minimal python-pip taskd gnutls-bin python-dev && \
    pip install pipenv && \
    pipenv sync && \
    rm -rf /var/lib/apt/lists/*

COPY . /usr/src/redshirt/

EXPOSE 4000
VOLUME /var/lib/taskd
ENV TASKDDATA="/var/lib/taskd"


CMD ["pipenv", "run", "gunicorn", "-b 0.0.0.0:4000", "redshirt:app"]