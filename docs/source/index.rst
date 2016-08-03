.. taskd-redshirt documentation master file, created by
   sphinx-quickstart on Mon Jul 11 18:11:58 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to redshirt's documentation!
==========================================

.. toctree::
   :maxdepth: 2

``redshirt`` is a http api for taskd user management. 
It should be placed on a closed port or bound to localhost or you may use Docker.


Installation
============

redshirt is on the cheeseshop! simply::

    pip install redshirt


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

``python redshirt.py <-b>``


Options
-------
  * :option:`-b` -- IP address to bind to. passed directly to ``bottle.run`` -- Default: 0.0.0.0

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

