from __future__ import with_statement
from invoke import task
import env, utils

@task(help={'passwd': "skp user password for sending ssh key to each host."})
def copy(c, passwd):
    for k, v in env.hosts.iteritems():
        cmd = "sudo sh -c 'echo {} {} >> /etc/hosts'".format(v["ipv4"], k)
        utils.run_with_exit(c, cmd)

    SKP_PASSWD = passwd
    SKP_MNAME, SKP_MIP = utils.get_mhost(env.hosts)
    for k, v in env.hosts.iteritems():
        cmd = "sshpass -p {} scp -o StrictHostKeyChecking=no /etc/hosts {}@{}:/tmp/hosts".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        utils.run_with_exit(c, cmd)

        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} sudo cp /tmp/hosts /etc/hosts".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        utils.run_with_exit(c, cmd)
