from __future__ import with_statement
from invoke import task
import env, utils, os

@task
def install(c):
    ports = [2049]

    cmd = "sudo apt-get install -y nfs-kernel-server portmap"
    utils.run_with_exit(c, cmd)

    for k, v in env.hosts.iteritems():
        for port in ports:
            cmd = "ssh -o StrictHostKeyChecking=no {}@{} sudo ufw allow {}".format(env.SKP_USER, v["ipv4"], port)
            utils.run_with_exit(c, cmd)

            cmd = "ssh -o StrictHostKeyChecking=no {}@{} sudo apt-get install -y nfs-common".format(env.SKP_USER, v["ipv4"])
            utils.run_with_exit(c, cmd)

@task
def exportfs(c, name=""):
    volumes = utils.get_volumes(env.volumes, name)
    for vk, vv in volumes.iteritems():
        if vv["type"] != "nfs":
            continue

        cmd = "mkdir -p {}".format(os.path.expandvars(vv["path"]))
        utils.run_with_exit(c, cmd)

    cmds = [
        "sudo exportfs -a",
        "showmount -e"
    ]
    for cmd in cmds:
        utils.run_with_exit(c, cmd)

@task
def restart(c):
    cmd = "sudo service nfs-kernel-server restart"
    utils.run_with_exit(c, cmd)
