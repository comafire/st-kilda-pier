from __future__ import with_statement

import os, sys, json, re
from pprint import pprint

# SKP
SKP_USER = os.environ["SKP_USER"]
SKP_HOME = os.environ["SKP_HOME"]
SKP_MNT = os.environ["SKP_MNT"]
SKP_HOSTS = os.environ["SKP_HOSTS"]
SKP_IMAGES = os.environ["SKP_IMAGES"]
SKP_NETWORKS = os.environ["SKP_NETWORKS"]
SKP_SERVICES = os.environ["SKP_SERVICES"]
SKP_VOLUMES = os.environ["SKP_VOLUMES"]

SKP_SUSER = os.environ["SKP_SUSER"]
SKP_SHOME = os.environ["SKP_SHOME"]
SKP_SMNT = os.environ["SKP_SMNT"]

images = {}
with open("{}".format(SKP_IMAGES)) as f:
    images = json.load(f)
    # pprint(nodes)

networks = {}
with open("{}".format(SKP_NETWORKS)) as f:
    networks = json.load(f)
    # pprint(nodes)

hosts = {}
with open("{}".format(SKP_HOSTS)) as f:
    hosts = json.load(f)
    # pprint(nodes)

volumes = {}
with open("{}".format(SKP_VOLUMES)) as f:
    volumes = json.load(f)
    # pprint(nodes)

services = {}
with open("{}".format(SKP_SERVICES)) as f:
    services = json.load(f)
    # pprint(nodes)
