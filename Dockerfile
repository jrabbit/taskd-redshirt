FROM debian:stretch
MAINTAINER Jack Laxson <jackjrabbit@gmail.com>

RUN mkdir -p /usr/src/redshirt

RUN apt-get update && apt-get install -y curl taskd gnutls-bin python-minimal && \
    curl -fSL 'https://bootstrap.pypa.io/get-pip.py' | python2 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install bottle==0.12.9

COPY . /usr/src/redshirt/

EXPOSE 4000
VOLUME /var/lib/taskd
ENV TASKDDATA="/var/lib/taskd"

WORKDIR /var/lib/taskd

CMD ["python2.7",  "/usr/src/redshirt/redshirt.py"]