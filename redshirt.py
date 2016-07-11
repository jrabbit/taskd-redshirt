import logging
import os
import shutil
from subprocess import check_output

from bottle import request, route, run, static_file, template

logger = logging.getLogger(__name__)

# saome feature ideas from paul
#17:56 <pbeckingham> jrabbit: When do my certs expire?
#17:57 <pbeckingham> jrabbit: Update CIPHERS
#17:57 <pbeckingham> jrabbit: Is there a new version available?
#17:57 <pbeckingham> jrabbit: User wipe

#17:58 <pbeckingham> jrabbit: Is it running?
# maybe as healthcheck for taskd?

# Renew Certs

@route("/add_user/<org>/<name>")
def add_user(org, name):
    o = check_output(["taskd", "add", "user", org, name])
    uuid = o.split('\n')[0].split()[-1]
    print uuid
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

if __name__ == '__main__':
    logging.basicConfig()
    run(host='0.0.0.0', port=int(os.environ.get("PORT", 4000)))
