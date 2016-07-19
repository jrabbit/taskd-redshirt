import logging
import os
import shutil
import socket
from subprocess import check_output

import baker
import psutil
from bottle import request, route, run, static_file, template

__version__ = "0.1.0a1"
logger = logging.getLogger(__name__)

# some feature ideas from paul
#17:56 <pbeckingham> jrabbit: When do my certs expire?
#17:57 <pbeckingham> jrabbit: Update CIPHERS
#17:57 <pbeckingham> jrabbit: Is there a new version available?
#17:57 <pbeckingham> jrabbit: User wipe

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
    l = x.strip().split("\n")[0]
    # '\x1b[1mtaskd 1.2.0\x1b[0m e2d145b built for linux'
    g = l.split()
    return {"version": g[1].split("\x1b")[0], "platform": g[-1], "git_rev": g[2]}

@route("/")
def index():
    hostname = socket.gethostname()
    return "<h1>Welcome to redshirt on {}.<h1>".format(hostname)

@route("/add_user/<org>/<name>")
def add_user(org, name):
    # may fail if group doesn't exist.
    o = check_output(["taskd", "add", "user", org, name])
    uuid = o.split('\n')[0].split()[-1]
    print(uuid)
    return uuid

@route("/create_cert/<user>")
def create_cert(user):
    """Creates a user cert/key pair with certtool and the taskd pki package."""
    check_output(['bash', './generate.client', user], cwd="/var/lib/taskd/pki/")
    logger.info(user)
    cert = "/var/lib/taskd/pki/{}.cert.pem".format(user)
    key = "/var/lib/taskd/pki/{}.key.pem".format(user)
    with open(cert) as f_cert, open(key) as f_key:
        d = {
            'certificate': f_cert.read(),
            'key': f_key.read()
        }
    cert_dst = "/var/lib/taskd/{}.cert.pem".format(user)
    if os.path.exists(cert_dst):
        logger.info("Overwriting: %s", cert_dst)
        os.remove(cert_dst)
    shutil.move(os.path.join("/var/lib/taskd/pki","{}.cert.pem".format(user)), "/var/lib/taskd/")
    os.remove("/var/lib/taskd/pki/{}.key.pem".format(user))
    # Delete useless certtool template file
    os.remove("/var/lib/taskd/pki/{}.template".format(user))
    return d


@route("/install_cert/", method="POST")
def install_cert():
    """Install an externally generated cert"""
    cert = request.POST.get("cert")
    uuid = request.POST.get("uuid")
    p = os.path.join("/var/lib/taskd", "{0}.cert.pem".format(uuid))
    with open(p, 'w') as f:
        f.write(cert)
    return "OK"

@route("/user/<user>", method="DELETE")
def remove_user(user, org):
    yolo = check_output(["taskd", "remove", user, org])


@baker.command(default=True)
def main(host='0.0.0.0'):
    logging.basicConfig()
    run(host=host, port=int(os.environ.get("PORT", 4000)),reloader=True)

if __name__ == '__main__':
    baker.run()
