from __future__ import with_statement

import os, sys, json, re
from pprint import pprint

def get_master(hosts):
    for k, v in hosts.iteritems():
        if "master" in v["roles"]:
            return k, v

def get_slaves(hosts):
    slaves = {}
    for k, v in hosts.iteritems():
        if "slave" in v["roles"]:
            continue
        slaves[k] = v
    return slaves

def get_manager(hosts):
    for k, v in hosts.iteritems():
        if "manager" in v["roles"]:
            return k, v

def get_workers(hosts):
    workers = {}
    for k, v in hosts.iteritems():
        if "worker" in v["roles"]:
            continue
        workers[k] = v
    return workers

def get_hosts(hosts, label):
    lhosts = {}
    for k, v in hosts.iteritems():
        for lk, lv in v["labels"].iteritems():
            if lk == label and lv == "enable":
                lhosts[k] = v
    return lhosts

def get_networks(networks, name):
    nets = {}
    if not name:
        nets = networks
    else:
        for nk, nv in networks.iteritems():
            if nk == name:
                nets[nk] = nv
    return nets

def get_volumes(volumes, name):
    vols = {}
    if not name:
        vols = volumes
    else:
        for vk, vv in volumes.iteritems():
            if vk == name:
                vols[vk] = vv
    return vols

def get_volume(volumes, name):
    for vk, vv in volumes.iteritems():
        if vk == name:
            return vk, vv

def get_service(services, name):
    for k, v in services.iteritems():
        if k == name:
            return k, v
    print("Not Found Service: {}".format(name))
    sys.exit(-1)

def get_image(images, name):
    for k, v in images.iteritems():
        if k == name:
            return k, v
    print("Not Found Image: {}".format(name))
    sys.exit(-1)

def get_images(images, name):
    imgs = {}
    if not name:
        imgs = images
    else:
        for ik, iv in images.iteritems():
            if ik == name:
                imgs[ik] = iv
    return imgs

def run_with_exit(c, cmd):
    res = c.run(cmd, warn=True)
    if res.failed:
        print("Fail to Run: {}".format(res.stderr.strip()))
        sys.exit(-1)
    return res.stdout.strip()

def run_without_exit(c, cmd):
    res = c.run(cmd, warn=True)
    if res.failed:
        print("Fail to Run: {}".format(res.stderr.strip()))
    return res.stdout.strip()

def run_mkdir(c, path):
    cmd = "sudo mkdir -p {} ".format(path)
    run_with_exit(c, cmd)

def run_rmdir(c, path):
    cmd = "sudo rm -rf {} ".format(path)
    run_with_exit(c, cmd)
