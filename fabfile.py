from fabric.api import *
from fabric.contrib import project

@task
def update_deps():
    local("docker pull debian") # for redshirt

docker_name = "gcr.io/stable-dogfish-697/redshirt:latest"

@task
def build():
    local("docker build -t {}".format(docker_name))

@task
def push():
    local("docker push {}".format(docker_name))

@task
def login():
    local("docker login -u oauth2accesstoken -p '$(gcloud auth print-access-token)' https://gcr.io")