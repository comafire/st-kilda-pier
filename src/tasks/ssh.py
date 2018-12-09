from __future__ import with_statement
from invoke import task
import env, utils

@task(help={'passwd': "skp user password for sending ssh key to each host."})
def copy_id(c, passwd):
    SKP_PASSWD = passwd
    mk, mv = utils.get_master(env.hosts)
    SKP_MIP = mv['ipv4']
    for k, v in env.hosts.iteritems():
        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} sudo apt-get update".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        utils.run_with_exit(c, cmd)

        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} sudo apt-get install -y sshpass".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        utils.run_with_exit(c, cmd)

        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} sudo sed -i -e 's/#AuthorizedKeysFile/AuthorizedKeysFile/g' /etc/ssh/sshd_config".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        utils.run_with_exit(c, cmd)

    for k, v in env.hosts.iteritems():
        # Generate Keys
        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} ".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        cmd += '"mkdir -p $HOME/.ssh;rm -f $HOME/.ssh/id_rsa;rm -f $HOME/.ssh/id_rsa.pub;'
        cmd += 'ssh-keygen -t rsa -N'
        cmd += " '' "
        cmd += '-f $HOME/.ssh/id_rsa"'
        utils.run_with_exit(c, cmd)

        # Send Master Public Key to All Hosts
        cmd = "sshpass -p {} ssh-copy-id -f -i $HOME/.ssh/id_rsa.pub -o StrictHostKeyChecking=no {}@{}".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        utils.run_with_exit(c, cmd)

    for k, v in env.hosts.iteritems():
        # Send All Node's Public Key to Master
        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} ".format(SKP_PASSWD, env.SKP_USER, v["ipv4"])
        cmd += "sshpass -p {} ssh-copy-id -f -i $HOME/.ssh/id_rsa.pub -o StrictHostKeyChecking=no {}@{}".format(SKP_PASSWD, env.SKP_USER, SKP_MIP)
        utils.run_with_exit(c, cmd)

@task
def cmd(c, cmd, host=""):
    if host:
        rcmd = "ssh -o StrictHostKeyChecking=no {}@{} {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
        utils.run_with_exit(c, rcmd)
    else:
        for k, v in env.hosts.iteritems():
            rcmd = "ssh -o StrictHostKeyChecking=no {}@{} {}".format(env.SKP_USER, v["ipv4"], cmd)
            utils.run_with_exit(c, rcmd)
