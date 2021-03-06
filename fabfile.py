from fabric.api import task, local 

@task
def update_deps():
    local("docker pull debian:stretch") # for redshirt

docker_name = "gcr.io/stable-dogfish-697/redshirt:latest"

@task
def build():
    local("docker build -t {} .".format(docker_name))

@task
def push():
    local("docker push {}".format(docker_name))

@task
def publish():
    local("docker tag {} jrabbit/redshirt".format(docker_name))
    local("docker push jrabbit/redshirt")

@task
def outdated():
    local("docker run -it --rm {} pipenv run pip list -o --format=columns".format(docker_name))

@task
def apt_outdated():
    local("docker run -it --rm {} bash -c 'apt-get update && apt list --upgradable'".format(docker_name))

@task
def login():
    local("gcloud docker -a")

@task
def docsauto():
    local("sphinx-autobuild -p 4444 -B -b html -d docs/build/doctrees   docs/source build/html")