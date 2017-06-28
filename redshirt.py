#!/usr/bin/env python

import logging
import os
import shutil
import socket
from subprocess import check_output

import baker
import packaging.version
import psutil
import requests
from bottle import request, route, run, static_file, template

__version__ = "0.1.0a2"
logger = logging.getLogger(__name__)
DATA_DIR = os.getenv("TASKDDATA", "/var/lib/taskd")

# some feature ideas from paul
#17:56 <pbeckingham> jrabbit: When do my certs expire?
#17:57 <pbeckingham> jrabbit: Update CIPHERS
#17:57 <pbeckingham> jrabbit: Is there a new version available?

#17:58 <pbeckingham> jrabbit: Is it running?

# Renew Certs

@route("/meta/version")
def version():
    return __version__

@route("/meta/health")
def self_health_check():
    return "OK"

def _get_proc():
    taskds = [x for x in psutil.process_iter() if "taskd" ==  x.name()]
    return taskds

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
    x = check_output(["taskd", "-v"])
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
    o = check_output(["taskd", "add", "user", org, name])
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
    yolo = check_output(["taskd", "remove", "user", org, user])
    return "OK"

@route("/user_data/<org>/<uuid>", method="DELETE")
def wipe_data(org, uuid):
    shutil.rmtree(os.path.join(DATA_DIR, "orgs", org, uuid))
    return "OK"

@route("/org/<org>", method="POST")
def add_org(org):
    check_output(["taskd", "add", "org", org])
    return "OK"


@route("/org/<org>", method="DELETE")
def rm_org(org):
    check_output(["taskd", "remove", "org", org])
    return "OK"

@baker.command(default=True, shortopts={"host": "b",})
def main(host='0.0.0.0'):
    # app = bottle.app()
    # if os.getenv("OPBEAT", False):
    #     app.catchall = False #Now most exceptions are re-raised within bottle.
    #     opbeat_client = Client(organization_id=os.getenv(OPBEAT_ORG_ID),
    #                            app_id=os.getenv(OPBEAT_ORG_ID),
    #                            secret_token=os.getenv(OPBEAT_ORG_ID))
    #     app = Opbeat(app, opbeat_client) #Replace this with a middleware of your choice (see below)
    
    logging.basicConfig()
    run(host=host, port=int(os.getenv("PORT", 4000)),reloader=True)

if __name__ == '__main__':
    baker.run()
