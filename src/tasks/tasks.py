from invoke import Collection

import iptable, host, ssh, lang, docker, nfs, sshfs, s3fs, blobfs

ns = Collection()
ns.add_collection(Collection.from_module(iptable))
ns.add_collection(Collection.from_module(host))
ns.add_collection(Collection.from_module(ssh))
ns.add_collection(Collection.from_module(lang))
ns.add_collection(Collection.from_module(docker))
ns.add_collection(Collection.from_module(nfs))
ns.add_collection(Collection.from_module(sshfs))
ns.add_collection(Collection.from_module(s3fs))
ns.add_collection(Collection.from_module(blobfs))
