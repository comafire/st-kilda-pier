from __future__ import with_statement

import os, sys, json, re
from pprint import pprint

def get_mhost(hosts):
    for k, v in hosts.iteritems():
        if "master" in v["groups"]:
            return k, v["ipv4"]

def get_ip(hosts, host):
    for k, v in hosts.iteritems():
        if k == host:
            return v["ipv4"]

def run_with_exit(c, cmd):
    res = c.run(cmd)
    if res.failed:
        print("Fail to Run: {}".format(res.stderr.strip()))
        os.exit(-1)

def get_nodes(hosts, label):
    nodes = []
    for k, v in hosts.iteritems():
        for l in v["labels"]:
            for lk, lv in l.iteritems():
                if lk == label and lv == "enable":
                    nodes.append(k)
    return nodes

def run_mkdir(c, path):
    cmd = "sudo mkdir -p {} ".format(path)
    run_with_exit(c, cmd)

def run_rmdir(c, path):
    cmd = "sudo rm -rf {} ".format(path)
    run_with_exit(c, cmd)
