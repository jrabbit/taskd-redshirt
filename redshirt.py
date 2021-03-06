#!/usr/bin/env python

import logging
import os
import shutil
import socket
import time
from datetime import datetime
from subprocess import check_output

import attr
import click
import packaging.version
import psutil
import requests
from bottle import (HTTPError, default_app, hook, install, request, response,
                    route, run, static_file, template)
from influxdb import InfluxDBClient
from raven import Client
from raven.contrib.bottle import Sentry

__version__ = "0.3.0b1"
logger = logging.getLogger(__name__)
DATA_DIR = os.getenv("TASKDDATA", "/var/lib/taskd")

# some feature ideas from paul
# 17:56 <pbeckingham> jrabbit: When do my certs expire?
# 17:57 <pbeckingham> jrabbit: Update CIPHERS
# 17:57 <pbeckingham> jrabbit: Is there a new version available?

# 17:58 <pbeckingham> jrabbit: Is it running?

# Renew Certs


@route("/meta/version")
def version():
    return __version__


@route("/meta/health")
def self_health_check():
    return "OK"


def _get_proc():
    taskds = [x for x in psutil.process_iter() if "taskd" == x.name()]
    return taskds


def _call_or_503(cmd):
    try:
        return check_output(cmd)
    except OSError as e:
        logger.error(
            "You don't seem to have taskd installed? Check your $PATH.", exc_info=True)
        raise HTTPError(
            status=503, body="You don't seem to have taskd installed? Check your $PATH.")


@route("/health")
def health_check():
    """Returns one of https://pythonhosted.org/psutil/#psutil.STATUS_RUNNING"""
    taskds = _get_proc()
    if len(taskds) > 1:
        raise NotImplementedError
    elif len(taskds) == 0:
        return {"status": "not running"}
    else:
        return {"status": taskds[0].status()}


@route("/version")
def get_version():
    """this is actually complicated if we're in a container environment.
       Maybe use taskc?!"""
    x = _call_or_503(["taskd", "-v"])
    l = x.strip().splitlines()[0]
    # print(l)
    # '\x1b[1mtaskd 1.2.0\x1b[0m e2d145b built for linux'
    g = l.split()
    return {"version": g[1].split(b"\x1b")[0], "platform": g[-1], "git_rev": g[2]}


def check_for_update():
    ret = requests.get("https://tasktools.org/latest/taskd")
    remote_version = packaging.version.parse(ret.text)
    local_version = packaging.version.parse(get_version()["version"])
    logger.debug("Comparing (local) %s and (remote) %s versions of taskd",
                 local_version, remote_version)
    if remote_version > local_version:
        return True
    else:
        return False


@route("/")
def index():
    hostname = socket.gethostname()
    return "<h1>Welcome to redshirt on {}.<h1>".format(hostname)


@route("/add_user/<org>/<name>")
def add_user(org, name):
    # may fail if group doesn't exist.
    o = _call_or_503(["taskd", "add", "user", org, name])
    uuid = o.split('\n')[0].split()[-1]
    logging.info("Created account on taskd: %s", uuid)
    return uuid


@route("/create_cert/<user>")
def create_cert(user):
    """Creates a user cert/key pair with certtool and the taskd pki package."""
    pki_path = os.path.join(DATA_DIR, "pki/")
    check_output(['bash', './generate.client', user], cwd=pki_path)
    logger.info(user)
    cert = os.path.join(pki_path, "{}.cert.pem".format(user))
    key = os.path.join(pki_path, "{}.key.pem".format(user))
    with open(cert) as f_cert, open(key) as f_key:
        d = {
            'certificate': f_cert.read(),
            'key': f_key.read()
        }
    cert_dst = "/var/lib/taskd/{}.cert.pem".format(user)
    if os.path.exists(cert_dst):
        logger.info("Overwriting: %s", cert_dst)
        os.remove(cert_dst)
    shutil.move(os.path.join(pki_path, "{}.cert.pem".format(user)), DATA_DIR)
    os.remove(os.path.join(pki_path, "{}.key.pem".format(user)))
    # Delete useless certtool template file
    os.remove(os.path.join(pki_path, "{}.template".format(user)))
    return d


@route("/install_cert/", method="POST")
def install_cert():
    """Install an externally generated cert"""
    cert = request.POST.get("cert")
    uuid = request.POST.get("uuid")
    p = os.path.join(DATA_DIR, "{0}.cert.pem".format(uuid))
    with open(p, 'w') as f:
        f.write(cert)
    return "OK"


@route("/user/<org>/<user>", method="DELETE")
def remove_user(user, org):
    _call_or_503(["taskd", "remove", "user", org, user])
    return "OK"


@route("/user_data/<org>/<uuid>", method="DELETE")
def wipe_data(org, uuid):
    shutil.rmtree(os.path.join(DATA_DIR, "orgs", org, uuid))
    return "OK"


@route("/org/<org>", method="POST")
def add_org(org):
    _call_or_503(["taskd", "add", "org", org])
    return "OK"


@route("/org/<org>", method="DELETE")
def rm_org(org):
    _call_or_503(["taskd", "remove", "org", org])
    return "OK"


@click.command()
@click.option('--debug', default=False, is_flag=True)
@click.option('--verbose/--silent', default=True)
@click.option('--port', default=4000)
@click.option("--host", default='0.0.0.0')
def main(host, port, verbose, debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    if verbose:
        logging.basicConfig(level=logging.INFO)

    run(host=host, port=int(os.getenv("PORT", port)), reloader=True)


@attr.s
class InfluxClientele(object):
    influx_host = attr.ib(default=os.getenv("INFLUX_HOST", "telegraf")) # assume container/compose env
    influx_user = attr.ib(default=None)
    influx_password = attr.ib(default=None)
    influx_database = attr.ib(default="telegraf")
    influx_port = attr.ib(default=os.getenv("INFLUX_PORT" ,8086)) # This is the influx direct port telegraf uses 8094
    reporting_host = attr.ib(default=socket.gethostname())

    def __attrs_post_init__(self):
        if True:
            self.client = InfluxDBClient(self.influx_host, self.influx_port, self.influx_user, self.influx_password, self.influx_database, use_udp=True, udp_port=8094)
        else:
            self.client = InfluxDBClient(self.influx_host, self.influx_port, self.influx_user, self.influx_password, self.influx_database)

    def begin_transaction(self, txn_type):
        self.start = time.time()
        self.txn_type = txn_type

    def end_transaction(self, path, status):
        # send txn to influx now
        end = time.time()
        duration = (end - self.start) * 1000
        self._send_txn_to_influx(path, status, duration)

    def _send_txn_to_influx(self, path, status, duration):
        # logger.debug("entered _send_txn_to_influx")
        data = [{"measurement": "redshirt_request",
                 "tags": {"type": self.txn_type,
                          "host": self.reporting_host,
                          "status_code": status,
                          "path": path, },
                 "time": datetime.now(),
                 "fields": {
                     "value": duration,
                 }}]
        self.client.write_points(data)

logging.basicConfig(level=logging.DEBUG)
app = default_app()
if os.getenv("REDSHIRT_TICK", False):
    client = InfluxClientele()
    @hook("after_request")
    def close_txn():
        client.end_transaction(request.path, response.status_code)

    @hook("before_request")
    def open_txn():
        client.begin_transaction("web.bottle")

    logger.info("telegraf APM enabled!")
    # app.catchall = False  # Now most exceptions are re-raised within bottle.

if os.getenv("SENTRY_URL", False):
    raven_client = Client(os.getenv("SENTRY_URL"))
    app = Sentry(app, raven_client)

if __name__ == '__main__':
    main()
