from invoke import Collection

import iptable
import ssh
import lang
import nfs
import docker
import fuse
import vagrant

ns = Collection()
ns.add_collection(Collection.from_module(iptable))
ns.add_collection(Collection.from_module(ssh))
ns.add_collection(Collection.from_module(lang))
ns.add_collection(Collection.from_module(nfs))
ns.add_collection(Collection.from_module(docker))
ns.add_collection(Collection.from_module(fuse))
ns.add_collection(Collection.from_module(vagrant))
