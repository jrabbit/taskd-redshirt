FROM debian:stretch
MAINTAINER Jack Laxson <jackjrabbit@gmail.com>

RUN mkdir -p /usr/src/redshirt


COPY requirements.txt /usr/src/redshirt

RUN apt-get update && apt-get install -y curl python2.7-minimal python-pip taskd gnutls-bin python-dev && \
    curl -fSL 'https://bootstrap.pypa.io/get-pip.py' | python2 && \
    pip install --no-cache-dir -r /usr/src/redshirt/requirements.txt && \
    rm -rf /var/lib/apt/lists/*

COPY . /usr/src/redshirt/

EXPOSE 4000
VOLUME /var/lib/taskd
ENV TASKDDATA="/var/lib/taskd"

WORKDIR /var/lib/taskd

CMD ["python2.7",  "/usr/src/redshirt/redshirt.py"]