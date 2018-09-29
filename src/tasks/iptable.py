from __future__ import with_statement
from invoke import task
import env, utils

@task
def masquerade(c):
    host_string = "127.0.0.1"
    cmd = "sudo /sbin/iptables -A FORWARD -o {} -j ACCEPT".format(env.SKP_PUB_ETH)
    utils.run_with_exit(c, cmd)
    cmd = "sudo sh -c 'echo {} >> /etc/init.d/ipmasq'".format(cmd)
    utils.run_with_exit(c, cmd)
    cmd = "sudo /sbin/iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format(env.SKP_PUB_ETH)
    utils.run_with_exit(c, cmd)
    cmd = "sudo sh -c 'echo {} >> /etc/init.d/ipmasq'".format(cmd)
    utils.run_with_exit(c, cmd)
    cmd = "sudo chmod 755 /etc/init.d/ipmasq"
    utils.run_with_exit(c, cmd)
    cmd = "sudo sh -c 'sudo update-rc.d ipmasq defaults'"
    utils.run_with_exit(c, cmd)
