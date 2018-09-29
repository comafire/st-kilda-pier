from __future__ import with_statement
from invoke import task
import env, utils

@task
def init(c):
    utils.run_mkdir(c, "{}/volume/etc/s3".format(env.SKP_HOME))
    utils.run_rmdir(c, "{}/volume/etc/s3/s3-passwd".format(env.SKP_HOME))
    cmd = "sudo bash -c \"echo {}:{} >> {}/volume/etc/s3/s3-passwd\"".format(env.S3_ACCESS_ID, env.S3_ACCESS_KEY, env.SKP_HOME)
    utils.run_with_exit(c, cmd)
    cmd = "sudo chmod 600 {}/volume/etc/s3/s3-passwd".format(env.SKP_HOME)
    utils.run_with_exit(c, cmd)
