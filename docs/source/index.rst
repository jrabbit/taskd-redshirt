.. taskd-redshirt documentation master file, created by
   sphinx-quickstart on Mon Jul 11 18:11:58 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to redshirt's documentation!
==========================================

.. toctree::
   :maxdepth: 2

``redshirt`` is a http api for taskd user management. 


Installation
============

redshirt is on the docker hub::

    docker pull jrabbit/redshirt




docker-compose
==============
.. note::
    This is how CGI uses redshirt!

your docker-compose.yml should look like

.. code-block:: yaml

    version: "2"
    services:
        # ... web etc go here
        redshirt:
            image: "jrabbit/redshirt:latest"
            volumes:
                - ./pki:/var/lib/taskd/pki
                - certs:/var/lib/taskd
            security_opt:
                - no-new-privileges
            healthcheck:
                test: curl -f http://localhost:4000/meta/health
                interval: 1m30s
                timeout: 10s
                retries: 3

        taskd:
            image: "jrabbit/taskd:latest"
            ports:
                - "53589:53589"
            volumes:
                - certs:/var/lib/taskd
    volumes:
        certs: {}


Usage
=====

Run ``gunicorn -b 0.0.0.0:4000 redshirt:app`` in ``/usr/src/redshirt``.
This is the default for the container! Make sure to forward port 4000 like ``-p 4000:4000``


Options
-------

See gunicorn_ for configuration options.

.. _gunicorn: http://docs.gunicorn.org/en/latest/run.html

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

