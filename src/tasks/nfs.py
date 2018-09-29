from __future__ import with_statement
from invoke import task
import env, utils

@task
def install(c):
    for k, v in env.hosts.iteritems():
        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "sudo apt-get install -y nfs-common nfs-kernel-server portmap"
        utils.run_with_exit(c, cmd)

@task
def mount_skp(c):
    SKP_MNAME, SKP_MIP = utils.get_mhost(env.hosts)
    for k, v in env.hosts.iteritems():
        if v["ipv4"] == SKP_MIP:
            continue

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "mkdir -p {}".format(env.SKP_HOME)
        utils.run_with_exit(c, cmd)

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "sudo mount -t nfs -o proto=tcp,port=2049 {}:{} {}".format(SKP_MIP, env.SKP_HOME, env.SKP_HOME)
        utils.run_with_exit(c, cmd)

@task
def umount_skp(c):
    SKP_MNAME, SKP_MIP = utils.get_mhost(env.hosts)
    for k, v in env.hosts.iteritems():
        if v["ipv4"] == SKP_MIP:
            continue

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} ".format(env.SKP_USER, v["ipv4"])
        cmd += "sudo umount {}".format(env.SKP_HOME)
        utils.run_with_exit(c, cmd)
