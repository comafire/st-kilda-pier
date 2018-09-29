from __future__ import with_statement
from invoke import task
import env, utils

@task
def keygen(c):
    utils.run_mkdir(c, "{}/volume/etc/ssh".format(env.SKP_HOME))
    cmd = "ssh-keygen -t rsa -N '' -f {}/volume/etc/ssh/id_rsa".format(env.SKP_HOME)
    utils.run_with_exit(c, cmd)

@task
def copy_id(c, passwd):
    SSHFS_PASSWD = passwd
    cmd = "sshpass -p {} ssh-copy-id -i {}/volume/etc/ssh/id_rsa.pub -o StrictHostKeyChecking=no {}@{}".format(SSHFS_PASSWD, env.SKP_HOME, env.SSHFS_ID, env.SSHFS_HOST)
    utils.run_with_exit(c, cmd)
