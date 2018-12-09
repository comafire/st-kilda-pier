from __future__ import with_statement
from invoke import task
import env, utils

@task(help={'eth': "public ethernet device name."})
def masquerade(c, eth):
    cmd = "sudo /sbin/iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format(eth)
    utils.run_with_exit(c, cmd)
    cmd = "sudo /sbin/iptables -A FORWARD -i {} -j ACCEPT".format(eth)
    utils.run_with_exit(c, cmd)
