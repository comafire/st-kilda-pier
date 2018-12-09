from __future__ import with_statement
from invoke import task
import env, utils, os

@task
def install(c):
    cmds = [
        "sudo apt-get update",
        "sudo apt-get install -y --no-install-recommends automake autotools-dev g++ git libcurl4-gnutls-dev libssl-dev libxml2-dev make pkg-config fuse libfuse-dev",
        "sudo apt-get install -y --no-install-recommends sshfs",
        "rm -rf s3fs-fuse",
        "git clone https://github.com/s3fs-fuse/s3fs-fuse.git",
        "\"cd s3fs-fuse && ./autogen.sh && ./configure && make && sudo make install\"",
        "rm -rf s3fs-fuse",
        "wget https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb",
        "sudo dpkg -i packages-microsoft-prod.deb",
        "rm -rf packages-microsoft-prod.deb",
        "sudo apt-get update",        
        "sudo apt-get install -y --no-install-recommends blobfuse"
    ]
    for hk, hv in env.hosts.iteritems():
        for cmd in cmds:
            rcmd = "ssh -o StrictHostKeyChecking=no {}@{} {}".format(env.SKP_USER, hv["ipv4"], cmd)
            utils.run_with_exit(c, rcmd)
