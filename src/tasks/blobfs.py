from __future__ import with_statement
from invoke import task
import env, utils

@task
def init(c):
    utils.run_mkdir(c, "{}/volume/etc/blob".format(env.SKP_HOME))
    utils.run_rmdir(c, "{}/volume/etc/blob/blob-passwd".format(env.SKP_HOME))
    cmd = "sudo bash -c \"echo 'accountName {}' >> {}/volume/etc/blob/blob-passwd\"".format(env.BLOB_ACCOUNT_NAME, env.SKP_HOME)
    utils.run_with_exit(c, cmd)
    cmd = "sudo bash -c \"echo 'accountKey {}' >> {}/volume/etc/blob/blob-passwd\"".format(env.BLOB_ACCOUNT_KEY, env.SKP_HOME)
    utils.run_with_exit(c, cmd)
    cmd = "sudo bash -c \"echo 'containerName {}' >> {}/volume/etc/blob/blob-passwd\"".format(env.BLOB_CONTAINER_NAME, env.SKP_HOME)
    utils.run_with_exit(c, cmd)
    cmd = "sudo chmod 600 {}/volume/etc/blob/blob-passwd".format(env.SKP_HOME)
    utils.run_with_exit(c, cmd)
