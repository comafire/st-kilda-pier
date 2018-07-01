from __future__ import with_statement
from fabric.api import *
from fabric.contrib.files import *
from fabric.operations import *
from fabric.contrib.console import confirm

import os, sys, json, re
from pprint import pprint

SKP_HOME = os.environ["SKP_HOME"]
SKP_HOSTS = os.environ["SKP_HOSTS"]
SKP_USER = os.environ["SKP_USER"]
SKP_PUB_ETH = os.environ["SKP_PUB_ETH"]
SKP_DFS = os.environ["SKP_DFS"]

SWARM_NET = os.environ["SWARM_NET"]

# Registry
REGISTRY_NAME = os.environ["REGISTRY_NAME"]
REGISTRY_PORT = os.environ["REGISTRY_PORT"]
REGISTRY_VOLUME = os.environ["REGISTRY_VOLUME"]
REGISTRY_IMAGE = os.environ["REGISTRY_IMAGE"]
REGISTRY_TAG = os.environ["REGISTRY_TAG"]

# SSHFS
SSHFS_ID = os.environ["SSHFS_ID"]
SSHFS_HOST = os.environ["SSHFS_HOST"]
SSHFS_VOLUME = os.environ["SSHFS_VOLUME"]

# S3FS
S3_ACCOUNT = os.environ["S3_ACCOUNT"]
S3_ACCESS_ID = os.environ["S3_ACCESS_ID"]
S3_ACCESS_KEY = os.environ["S3_ACCESS_KEY"]

# BLOBFS
BLOB_ACCOUNT_NAME = os.environ["BLOB_ACCOUNT_NAME"]
BLOB_ACCOUNT_KEY = os.environ["BLOB_ACCOUNT_KEY"]
BLOB_CONTAINER_NAME = os.environ["BLOB_CONTAINER_NAME"]

# Jupyter
JUPYTER_NAME = os.environ["JUPYTER_NAME"]
JUPYTER_PORT = os.environ["JUPYTER_PORT"]
JUPYTER_VOLUME = os.environ["JUPYTER_VOLUME"]
JUPYTER_PASSWORD = os.environ["JUPYTER_PASSWORD"]
JUPYTER_BASEURL = os.environ["JUPYTER_BASEURL"]
JUPYTER_RESTAPIPORT = os.environ["JUPYTER_RESTAPIPORT"]
JUPYTER_IMAGE = os.environ["JUPYTER_IMAGE"]
JUPYTER_TAG = os.environ["JUPYTER_TAG"]
JUPYTER_GPU_IMAGE = os.environ["JUPYTER_GPU_IMAGE"]
JUPYTER_GPU_TAG = os.environ["JUPYTER_GPU_TAG"]
JUPYTER_GPU = os.environ["JUPYTER_GPU"]

# Spark
SPARK_MNAME = os.environ["SPARK_MNAME"]
SPARK_WNAME = os.environ["SPARK_WNAME"]
SPARK_MPORT = os.environ["SPARK_MPORT"]
SPARK_VOLUME = os.environ["SPARK_VOLUME"]
SPARK_URL = os.environ["SPARK_URL"]
SPARK_IMAGE = os.environ["SPARK_IMAGE"]
SPARK_TAG = os.environ["SPARK_TAG"]
SPARK_GPU_IMAGE = os.environ["SPARK_GPU_IMAGE"]
SPARK_GPU_TAG = os.environ["SPARK_GPU_TAG"]
SPARK_GPU = os.environ["SPARK_GPU"]

# MySQL
MYSQL_NAME = os.environ["MYSQL_NAME"]
MYSQL_PORT = os.environ["MYSQL_PORT"]
MYSQL_IMAGE = os.environ["MYSQL_IMAGE"]
MYSQL_TAG = os.environ["MYSQL_TAG"]
MYSQL_VOLUME = os.environ["MYSQL_VOLUME"]
MYSQL_ROOT_PASSWORD = os.environ["MYSQL_ROOT_PASSWORD"]

# Airflow
AIRFLOW_NAME = os.environ["AIRFLOW_NAME"]
AIRFLOW_PORT = os.environ["AIRFLOW_PORT"]
AIRFLOW_VOLUME = os.environ["AIRFLOW_VOLUME"]
AIRFLOW_DB = os.environ["AIRFLOW_DB"]
AIRFLOW_DB_USER = os.environ["AIRFLOW_DB_USER"]
AIRFLOW_DB_PASSWORD = os.environ["AIRFLOW_DB_PASSWORD"]
AIRFLOW__CORE__SQL_ALCHEMY_CONN = os.environ["AIRFLOW__CORE__SQL_ALCHEMY_CONN"]
AIRFLOW_IMAGE = os.environ["AIRFLOW_IMAGE"]
AIRFLOW_TAG = os.environ["AIRFLOW_TAG"]
AIRFLOW_GPU_IMAGE = os.environ["AIRFLOW_GPU_IMAGE"]
AIRFLOW_GPU_TAG = os.environ["AIRFLOW_GPU_TAG"]
AIRFLOW_GPU= os.environ["AIRFLOW_GPU"]

# Portainer
PORTAINER_NAME = os.environ["PORTAINER_NAME"]
PORTAINER_PORT = os.environ["PORTAINER_PORT"]
PORTAINER_ID = os.environ["PORTAINER_ID"]
PORTAINER_PW = os.environ["PORTAINER_PW"]

# Zookeeper
ZOOKEEPER_NAME = os.environ["ZOOKEEPER_NAME"]
ZOOKEEPER_PORT = os.environ["ZOOKEEPER_PORT"]
ZOOKEEPER_VOLUME = os.environ["ZOOKEEPER_VOLUME"]
ZOOKEEPER_IMAGE = os.environ["ZOOKEEPER_IMAGE"]
ZOOKEEPER_TAG = os.environ["ZOOKEEPER_TAG"]

# Kafka
KAFKA_NAME = os.environ["KAFKA_NAME"]
KAFKA_PORT = os.environ["KAFKA_PORT"]
KAFKA_ADVERTISED_PORT = os.environ["KAFKA_ADVERTISED_PORT"]
KAFKA_VOLUME = os.environ["KAFKA_VOLUME"]
KAFKA_IMAGE = os.environ["KAFKA_IMAGE"]
KAFKA_TAG = os.environ["KAFKA_TAG"]

# Flask
FLASK_SECRET = os.environ["FLASK_SECRET"]
FLASK_VOLUME = os.environ["FLASK_VOLUME"]
FLASK_IMAGE = os.environ["FLASK_IMAGE"]
FLASK_TAG = os.environ["FLASK_TAG"]
FLASK_GPU_IMAGE = os.environ["FLASK_GPU_IMAGE"]
FLASK_GPU_TAG = os.environ["FLASK_GPU_TAG"]
FLASK_GPU= os.environ["FLASK_GPU"]

# Nginx
NGINX_VOLUME = os.environ["NGINX_VOLUME"]
NGINX_IMAGE = os.environ["NGINX_IMAGE"]
NGINX_TAG = os.environ["NGINX_TAG"]

env.hosts = []
env.user = SKP_USER
# env.key_filename = SKP_PRI_KEY
env.disable_known_hosts = True

with open(SKP_HOSTS) as f:
    hosts = json.load(f)
    #pprint(hosts)

def _check_result(result):
    if result.failed and not confirm("Command failed. Continue anyway?"):
        abort("Aborting at user request.")

@task
def test():
    result = local("ls -al")
    if result.failed and not confirm("Tests failed. Continue anyway?"):
        abort("Aborting at user request.")

@task
def iptables_masquerade():
    env.host_string = "127.0.0.1"
    cmd = "/sbin/iptables -A FORWARD -o {} -j ACCEPT".format(SKP_PUB_ETH)
    print(cmd)
    result = sudo(cmd)
    _check_result(result)
    append("/etc/rc.local", cmd, use_sudo=True, partial=True)

    cmd = "/sbin/iptables -t nat -A POSTROUTING -o {} -j MASQUERADE".format(SKP_PUB_ETH)
    print(cmd)
    result = sudo(cmd)
    _check_result(result)
    append("/etc/rc.local", cmd, use_sudo=True, partial=True)

@task
def ssh_keygen():
    local("mkdir -p {}/etc/ssh".format(SKP_HOME))
    for k, v in hosts.iteritems():
        print(k, v)
        cmd = "ssh-keygen -t rsa -N '' -f {}/etc/ssh/skp_{}_rsa".format(SKP_HOME, k)
        print(cmd)
        result = local(cmd)
        _check_result(result)

def _get_mhost():
    for k, v in hosts.iteritems():
        if ("master" in v["groups"]):
            return k, v["ipv4"]

@task
def ssh_copy_id():
    SKP_PASSWD = env.SKP_PASSWD
    if SKP_PASSWD == "":
        print("need password!!")
        return

    SKP_MNAME, SKP_MIP = _get_mhost()
    for k, v in hosts.iteritems():
        #print(k, v)
        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} sudo apt-get install -y sshpass".format(SKP_PASSWD, SKP_USER, v["ipv4"])
        print(cmd)
        result = local(cmd)
        _check_result(result)

        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} mkdir -p ~/.ssh".format(SKP_PASSWD, SKP_USER, v["ipv4"])
        print(cmd)
        result = local(cmd)
        _check_result(result)

        # copy key to each node
        cmd = "sshpass -p {} scp -o StrictHostKeyChecking=no {}/etc/ssh/skp_{}_rsa {}@{}:.ssh".format(SKP_PASSWD, SKP_HOME, k, SKP_USER, v["ipv4"])
        print(cmd)
        result = local(cmd)
        _check_result(result)

        cmd = "sshpass -p {} scp -o StrictHostKeyChecking=no {}/etc/ssh/skp_{}_rsa.pub {}@{}:.ssh".format(SKP_PASSWD, SKP_HOME, k, SKP_USER, v["ipv4"])
        print(cmd)
        result = local(cmd)
        _check_result(result)

        # exchnage key to each node
        cmd = "sshpass -p {} ssh-copy-id -i {}/etc/ssh/skp_{}_rsa.pub -o StrictHostKeyChecking=no {}@{}".format(SKP_PASSWD, SKP_HOME, SKP_MNAME, SKP_USER, v["ipv4"])
        print(cmd)
        result = local(cmd)
        _check_result(result)

        cmd = "sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} ".format(SKP_PASSWD, SKP_USER, v["ipv4"])
        cmd += "sshpass -p {} ssh-copy-id -i ~/.ssh/skp_{}_rsa.pub -o StrictHostKeyChecking=no {}@{}".format(SKP_PASSWD, k, SKP_USER, SKP_MIP)
        print(cmd)
        result = local(cmd)
        _check_result(result)

def _fuse_install():
    # install fuse
    cmd = "sudo apt-get update && sudo apt-get install -y --no-install-recommends "
    cmd += "automake autotools-dev g++ git libcurl4-gnutls-dev libssl-dev libxml2-dev make pkg-config "
    cmd += "fuse libfuse-dev"
    run(cmd)

    # install sshfs
    cmd = "sudo apt-get update && sudo apt-get install -y --no-install-recommends "
    cmd += "sshfs"
    run(cmd)

    # install s3fs
    # cmd = "mkdir -p ~/tmp"
    # run(cmd)
    #
    # cmd = "cd ~/tmp;git clone https://github.com/s3fs-fuse/s3fs-fuse.git;cd s3fs-fuse;./autogen.sh;./configure;make;sudo make install"
    # run(cmd)

    # install blobfs
    # cmd = "cd ~/tmp;wget https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb;"
    # cmd += "sudo dpkg -i packages-microsoft-prod.deb;"
    # cmd += "sudo apt-get update && sudo apt-get install -y --no-install-recommends blobfuse"
    # run(cmd)

def _get_mkey_filename():
    for k, v in hosts.iteritems():
        if ("master" in v["groups"]):
            return "{}/etc/ssh/skp_{}_rsa".format(SKP_HOME, k)

@task
def fuse_install():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_fuse_install, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result


@task
def sshfs_umount_skp():
    SKP_MNAME, SKP_MIP = _get_mhost()
    for k, v in hosts.iteritems():
        if "master" in v["groups"]:
            continue
        cmd = "ssh -i ~/.ssh/skp_{}_rsa -o StrictHostKeyChecking=no {}@{} ".format(SKP_MNAME, SKP_USER, v["ipv4"])
        cmd += "sudo umount {}".format(SKP_HOME)
        print(cmd)
        result = {}
        try:
            result = local(cmd)
        except:
            print(result)

@task
def sshfs_mount_skp():
    SKP_MNAME, SKP_MIP = _get_mhost()
    for k, v in hosts.iteritems():
        if "master" in v["groups"]:
            continue
        cmd = "ssh -i ~/.ssh/skp_{}_rsa -o StrictHostKeyChecking=no {}@{} ".format(SKP_MNAME, SKP_USER, v["ipv4"])
        #cmd += "sshfs {}@{}:{} {} -o uid=0,gid=0,nonempty,IdentityFile=~/.ssh/skp_{}_rsa -o StrictHostKeyChecking=no".format(SKP_USER, SKP_MIP, SKP_HOME, SKP_HOME, k)
        cmd += "sshfs {}@{}:{} {} -o nonempty,IdentityFile=~/.ssh/skp_{}_rsa -o StrictHostKeyChecking=no".format(SKP_USER, SKP_MIP, SKP_HOME, SKP_HOME, k)
        print(cmd)
        result = local(cmd)
        _check_result(result)

def _rcmd(RCMD):
    try:
        run(RCMD)
    except BaseException as e:
        print("Ignore Error")

@task
def rcmd():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_rcmd, env.RCMD, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _etc_hosts(etc_hosts):
    try:
	for etc_host in etc_hosts:
            append("/etc/hosts", etc_host, use_sudo=True, partial=True)
    except BaseException as e:
        return e

@task
def etc_hosts():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    etc_hosts = []
    for k, v in hosts.iteritems():
        #print(k, v)
        env.hosts.append(v["ipv4"])
        etc_hosts.append("%s\t%s" % (v["ipv4"], k))
    print(env.hosts)
    print(etc_hosts)

    result = {}
    try:
        result = execute(_etc_hosts, etc_hosts, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _nfs_install():
    try:
        sudo("apt-get install -y nfs-common nfs-kernel-server portmap")
    except BaseException as e:
        return e

@task
def nfs_install():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_nfs_install, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _nfs_mount_skp(SKP_MIP):
    try:
        run("mkdir -p {}".format(SKP_HOME))
    except BaseException as e:
        print("don't care")
    sudo("mount -t nfs -o proto=tcp,port=2049 {}:{} {}".format(SKP_MIP, SKP_HOME, SKP_HOME))

@task
def nfs_mount_skp():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    SKP_MIP = ""
    for k, v in hosts.iteritems():
        if "master" in v["groups"]:
            SKP_MIP = v["ipv4"]
            continue
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_nfs_mount_skp, SKP_MIP, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _nfs_umount_skp():
    try:
        sudo("umount {}".format(SKP_HOME))
    except BaseException as e:
        print("")

@task
def nfs_umount_skp():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        if "master" in v["groups"]:
            SKP_MIP = v["ipv4"]
            continue
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_nfs_umount_skp, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _ufw():
    ports = [22, 2376, 2377, 7946, 4789]
    try:
        for port in ports:
            sudo("ufw allow {}".format(port))
    except BaseException as e:
        return e

@task
def ufw():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_ufw, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

@task
def docker_machine_install():
    cmd = "curl -L https://github.com/docker/machine/releases/download/v0.13.0/docker-machine-`uname -s`-`uname -m` >/tmp/docker-machine && sudo install /tmp/docker-machine /usr/local/bin/docker-machine"
    return local(cmd)

@task
def docker_machine_create():
    SKP_MKEY = _get_mkey_filename()
    result = {}
    for k, v in hosts.iteritems():
        print(k, v)
        cmd = "docker-machine create --driver generic --generic-ip-address {} --generic-ssh-key {} --generic-ssh-user {} {}".format(v["ipv4"], SKP_MKEY, SKP_USER, k)
        print(cmd)
        try:
            result_sub = local(cmd)
        except BaseException as e:
            print("don't care")

    result["status"] = "SUCCESS"

    print(result)
    return result

def _docker_swarm_init(master):
    cmd = "docker swarm init --advertise-addr %s" % master
    return run(cmd)

@task
def docker_swarm_init():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        if "master" in v["groups"]:
            env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_docker_swarm_init, env.hosts[0], hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_swarm_join_token(group):
    cmd = "docker swarm join-token %s" % group
    return run(cmd)

def _docker_swarm_join(cmd):
    return run(cmd)

@task
def docker_swarm_join():
    env.key_filename = _get_mkey_filename()

    master = []
    managers = []
    workers = []
    for k, v in hosts.iteritems():
        #print(k, v)
        if ("master" in v["groups"]):
            master.append(v["ipv4"])
        if ("manager" in v["groups"]):
            if ("master" not in v["groups"]):
                managers.append(v["ipv4"])
        if ("worker" in v["groups"]):
            workers.append(v["ipv4"])

    print("master: %s" % master)
    print("managers: %s" % managers)
    print("workers: %s" % workers)

    result = {}
    try:
        output = execute(_docker_swarm_join_token, group="manager", hosts=master)
        cmd_manager = re.search(r'docker\sswarm\sjoin.*:[0-9]{4}', output[master[0]], re.DOTALL).group()
        cmd_manager = re.sub(r'[\\\r\n]', "", cmd_manager)
        output = execute(_docker_swarm_join_token, group="worker", hosts=master)
        cmd_worker = re.search(r'docker\sswarm\sjoin.*:[0-9]{4}', output[master[0]], re.DOTALL).group()
        cmd_worker = re.sub(r'[\\\r\n]', "", cmd_worker)

        output = execute(_docker_swarm_join, cmd=cmd_manager, hosts=managers)
        output = execute(_docker_swarm_join, cmd=cmd_worker, hosts=workers)

        result["status"] = "SUCCESS"
        return result
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"
        return result

def _docker_swarm_network(name):
    cmd = "docker network create --attachable --driver overlay %s" % name
    return run(cmd)

@task
def docker_swarm_network():
    env.key_filename = _get_mkey_filename()
    master = []

    for k, v in hosts.iteritems():
        #print(k, v)
        if ("master" in v["groups"]):
            master.append(v["ipv4"])

    result = {}
    try:
        result = execute(_docker_swarm_network, name=SWARM_NET, hosts=master)
        result["status"] = "SUCCESS"
        return result
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"
        return result

def _docker_swarm_label(label, node):
    cmd = "docker node update %s %s" % (label, node)
    return run(cmd)

@task
def docker_swarm_label():
    env.key_filename = _get_mkey_filename()

    master = []
    labels = {}
    for k, v in hosts.iteritems():
        #print(k, v)
        if ("master" in v["groups"]):
            master.append(v["ipv4"])
        labels[k] = ""
        for label in v["labels"]:
            for lk, lv in label.iteritems():
                labels[k] += " --label-add %s=%s " % (lk, lv)

    result = {}
    try:
        for k, v in labels.iteritems():
            output = execute(_docker_swarm_label, label=v, node=k, hosts=master)
        result["status"] = "SUCCESS"
        return result
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"
        return result

def _docker_compose_install():
    try:
        sudo("curl -L https://github.com/docker/compose/releases/download/1.19.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose")
        sudo("chmod +x /usr/local/bin/docker-compose")
    except BaseException as e:
        return e

@task
def docker_compose_install():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_docker_compose_install, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

@task
def docker_ps():
    for k, v in hosts.iteritems():
        cmd = "docker-machine ssh {} ".format(k)
        cmd += "docker ps"
        result = {}
        try:
            local(cmd)
            result["status"] = "SUCCESS"
        except BaseException as e:
            result["message"] = e
            result["status"] = "FAIL"

    print(result)
    return result

@task
def docker_images():
    for k, v in hosts.iteritems():
        cmd = "docker-machine ssh {} ".format(k)
        cmd += "docker images"
        local(cmd)

@task
def docker_build():
    result = {}
    try:
        cmd = "docker build --build-arg locale={} --build-arg gpu={} ".format(env.LOCALE, env.GPU)
        cmd += "{}/etc/docker-file/{} --tag {}:{} ".format(SKP_HOME, env.NAME, env.IMAGE, env.TAG)
        local(cmd)
        cmd = "docker image tag {}:{} localhost:5000/{}:{}".format(env.IMAGE, env.TAG, env.IMAGE, env.TAG)
        local(cmd)
        cmd = "docker push localhost:5000/{}:{}".format(env.IMAGE, env.TAG)
        local(cmd)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_pull_local(IMAGE, TAG):
    cmd = "docker pull localhost:5000/{}:{}".format(env.IMAGE, env.TAG)
    return run(cmd)

@task
def docker_pull_local():
    env.key_filename = _get_mkey_filename()
    env.hosts = []

    for k, v in hosts.iteritems():
        env.hosts.append(v["ipv4"])

    result = {}
    try:
        result = execute(_docker_pull_local, env.IMAGE, env.TAG, hosts=env.hosts)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result


@task
def docker_delete_registry_image():
    result = {}
    try:
        cmd = "curl https://raw.githubusercontent.com/burnettk/delete-docker-registry-image/master/delete_docker_registry_image.py | sudo tee /usr/local/bin/delete_docker_registry_image >/dev/null"
	local(cmd)
	cmd = "sudo chmod a+x /usr/local/bin/delete_docker_registry_image"
	local(cmd)
        cmd = "export REGISTRY_DATA_DIR={}/docker/registry/v2;delete_docker_registry_image --image {}:{} --dry-run".format(REGISTRY_VOLUME, env.IMAGE, env.TAG)
        local(cmd)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _get_nodes(label):
    nodes = []
    for k, v in hosts.iteritems():
        for l in v["labels"]:
            for lk, lv in l.iteritems():
                if lk == label and lv == "enable":
                    nodes.append(k)
    return nodes

def _docker_rm(nodes, name):
    for node in nodes:
        try:
            cmd = "docker-machine ssh {} ".format(node)
            cmd += "docker rm -f {} ".format(name)
            local(cmd)
        except BaseException as e:
            print("{}:{} is already removed".format(node, name))

def _docker_run(nodes, cmd):
    for node in nodes:
        rcmd = "docker-machine ssh {} ".format(node)
        rcmd += cmd
        local(rcmd)


def _local_mkdir(path):
    try:
        cmd = "sudo mkdir -p {} ".format(path)
        local(cmd)
    except BaseException as e:
        print("directory is already existed..")

def _run_mkdir(path):
    try:
        cmd = "sudo mkdir -p {} ".format(path)
        run(cmd)
    except BaseException as e:
        print("directory is already existed..")

@task
def docker_run_registry():
    nodes = _get_nodes("registry")
    result = {}
    _local_mkdir(REGISTRY_VOLUME)
    _docker_rm(nodes, REGISTRY_NAME)
    try:
        cmd = "docker run -i -t -d --name {} ".format(REGISTRY_NAME)
        cmd += "--restart=always --network {} ".format(SWARM_NET)
        cmd += "-p {}:5000 ".format(REGISTRY_PORT)
        cmd += "-v {}:/var/lib/registry ".format(REGISTRY_VOLUME)
        cmd += "{}:{}".format(REGISTRY_IMAGE, REGISTRY_TAG)
        _docker_run(nodes, cmd)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

@task
def docker_rm_registry():
    nodes = _get_nodes("registry")
    result = {}
    _docker_rm(nodes, REGISTRY_NAME)

@task
def sshfs_keygen():
    local("mkdir -p {}/volume/etc/ssh".format(SKP_HOME))
    cmd = "ssh-keygen -t rsa -N '' -f {}/volume/etc/ssh/id_rsa".format(SKP_HOME)
    print(cmd)
    result = local(cmd)
    _check_result(result)

@task
def sshfs_copy_id():
    SSHFS_PASSWD = env.SSHFS_PASSWD
    if SSHFS_PASSWD == "":
        print("need password!!")
        return

    cmd = "sshpass -p {} ssh-copy-id -i {}/volume/etc/ssh/id_rsa.pub -o StrictHostKeyChecking=no {}@{}".format(SSHFS_PASSWD, SKP_HOME, SSHFS_ID, SSHFS_HOST)
    print(cmd)
    result = local(cmd)
    _check_result(result)

@task
def s3fs_init():
    local("sudo mkdir -p {}/volume/etc/s3".format(SKP_HOME))
    local("sudo rm -f {}/volume/etc/s3/s3-passwd".format(SKP_HOME))
    local("sudo bash -c \"echo {}:{} >> {}/volume/etc/s3/s3-passwd\"".format(S3_ACCESS_ID, S3_ACCESS_KEY, SKP_HOME))
    local("sudo chmod 600 {}/volume/etc/s3/s3-passwd".format(SKP_HOME))

@task
def blobfs_init():
    local("sudo mkdir -p {}/volume/etc/blob".format(SKP_HOME))
    local("sudo rm -f {}/volume/etc/blob/blob-passwd".format(SKP_HOME))
    local("sudo bash -c \"echo 'accountName {}' >> {}/volume/etc/blob/blob-passwd\"".format(BLOB_ACCOUNT_NAME, SKP_HOME))
    local("sudo bash -c \"echo 'accountKey {}' >> {}/volume/etc/blob/blob-passwd\"".format(BLOB_ACCOUNT_KEY, SKP_HOME))
    local("sudo bash -c \"echo 'containerName {}' >> {}/volume/etc/blob/blob-passwd\"".format(BLOB_CONTAINER_NAME, SKP_HOME))
    local("sudo chmod 600 {}/volume/etc/blob/blob-passwd".format(SKP_HOME))

@task
def docker_run_jupyter():
    nodes = _get_nodes("jupyter")
    result = {}
    _docker_rm(nodes, JUPYTER_NAME)
    DOCKER = "docker"
    DOCKER_IMAGE = JUPYTER_IMAGE
    DOCKER_TAG = JUPYTER_TAG
    if JUPYTER_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = JUPYTER_GPU_IMAGE
        DOCKER_TAG = JUPYTER_GPU_TAG

    try:
        cmd = "{} run -i -t -d --name {} ".format(DOCKER, JUPYTER_NAME)
        cmd += "--privileged --restart=always --network {} ".format(SWARM_NET)
        cmd += "-p {}:8888 -p {}:8088 ".format(JUPYTER_PORT, JUPYTER_RESTAPIPORT)
        cmd += "-v /var/run/docker.sock:/var/run/docker.sock "
        cmd += "-v {}:/root/mnt/dfs ".format(SKP_DFS)
        cmd += "-v {}:/root/volume ".format(JUPYTER_VOLUME)
        cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(SSHFS_ID, SSHFS_HOST, SSHFS_VOLUME)
        cmd += "-e S3_ACCOUNT={} ".format(S3_ACCOUNT)
        cmd += "-e MYSQL_ROOT_PASSWORD={} ".format(MYSQL_ROOT_PASSWORD)
        cmd += "-e FLASK_SECRET={} ".format(FLASK_SECRET)
        cmd += "-e JUPYTER_BASEURL={} -e JUPYTER_PASSWORD={} ".format(JUPYTER_BASEURL, JUPYTER_PASSWORD)
        cmd += "localhost:5000/{}:{} /root/volume/bin/run_jupyter.sh".format(DOCKER_IMAGE, DOCKER_TAG)
        print(cmd)
        _docker_run(nodes, cmd)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_exec_shell(name):
    return run("docker exec -it {} /bin/bash".format(name))

@task
def docker_exec_shell():
    env.key_filename = _get_mkey_filename()
    return execute(_docker_exec_shell, name=env.NAME, hosts=env.HOST)

@task
def docker_rm_spark():
    master = _get_nodes("spark-master")
    workers = _get_nodes("spark-worker")
    _docker_rm(master, SPARK_MNAME)
    _docker_rm(workers, SPARK_WNAME)

@task
def docker_run_spark():
    master = _get_nodes("spark-master")
    workers = _get_nodes("spark-worker")
    result = {}
    _docker_rm(master, SPARK_MNAME)
    _docker_rm(workers, SPARK_WNAME)
    DOCKER = "docker"
    DOCKER_IMAGE = SPARK_IMAGE
    DOCKER_TAG = SPARK_TAG
    if JUPYTER_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = SPARK_GPU_IMAGE
        DOCKER_TAG = SPARK_GPU_TAG

    try:
        cmd = "{} run -i -t --name {} ".format(DOCKER, SPARK_MNAME)
        cmd += "-d --privileged --restart=always --network {} ".format(SWARM_NET)
        cmd += "-v {}:/root/mnt/dfs ".format(SKP_DFS)
        cmd += "-v {}:/root/volume ".format(SPARK_VOLUME)
        cmd += "-p {}:8080 ".format(SPARK_MPORT)
        cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(SSHFS_ID, SSHFS_HOST, SSHFS_VOLUME)
        cmd += "-e S3_ACCOUNT={} ".format(S3_ACCOUNT)
        cmd += "localhost:5000/{}:{} /root/volume/bin/run_spark_master.sh ".format(DOCKER_IMAGE, DOCKER_TAG)
        print(cmd)
        _docker_run(master, cmd)

        cmd = "docker run -i -t --name {} ".format(SPARK_WNAME)
        cmd += "-d --privileged --restart=always --network {} ".format(SWARM_NET)
        cmd += "-v {}:/root/mnt/dfs ".format(SKP_DFS)
        cmd += "-e SPARK_URL={} -v {}:/root/volume ".format(SPARK_URL, SPARK_VOLUME)
        cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(SSHFS_ID, SSHFS_HOST, SSHFS_VOLUME)
        cmd += "-e S3_ACCOUNT={} ".format(S3_ACCOUNT)
        cmd += "localhost:5000/{}:{} /root/volume/bin/run_spark_worker.sh".format(SPARK_IMAGE, SPARK_TAG)
        print(cmd)
        _docker_run(workers, cmd)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

@task
def docker_run_mysql():
    nodes = _get_nodes("mysql")
    result = {}
    _local_mkdir(MYSQL_VOLUME)
    _docker_rm(nodes, MYSQL_NAME)
    try:
        cmd = "docker run -i -t -d --name {} ".format(MYSQL_NAME)
        cmd += "--restart=always --network {} ".format(SWARM_NET)
        cmd += "-p {}:3306 ".format(MYSQL_PORT)
        cmd += "-e MYSQL_ROOT_PASSWORD={} ".format(MYSQL_ROOT_PASSWORD)
	cmd += "-e MYSQL_ROOT_HOST=% "
        cmd += "-v {}:/var/lib/mysql ".format(MYSQL_VOLUME)
        cmd += "{}:{} --default-authentication-plugin=mysql_native_password ".format(MYSQL_IMAGE, MYSQL_TAG)
        print(cmd)
        _docker_run(nodes, cmd)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_exec_mysql():
    return run('docker exec -it {} mysql -uroot -p"{}"'.format(MYSQL_NAME, MYSQL_ROOT_PASSWORD))

@task
def docker_exec_mysql():
    env.key_filename = _get_mkey_filename()

    nodes = _get_nodes("mysql")
    return execute(_docker_exec_mysql, hosts=nodes)

def _docker_init_airflow_mysql():
    SQL = "CREATE DATABASE {};".format(AIRFLOW_DB)
    SQL += "CREATE USER '{}'@'%' IDENTIFIED BY '{}';".format(AIRFLOW_DB_USER, AIRFLOW_DB_PASSWORD)
    SQL += "GRANT ALL PRIVILEGES ON {}.* TO '{}'@'%';".format(AIRFLOW_DB, AIRFLOW_DB_USER)
    SQL += "FLUSH PRIVILEGES;"
    cmd = 'docker exec -it {} mysql -uroot -p"{}" -e"{}"'.format(MYSQL_NAME, MYSQL_ROOT_PASSWORD, SQL)
    print(cmd)
    run(cmd)

@task
def docker_init_airflow_mysql():
    env.key_filename = _get_mkey_filename()

    nodes = _get_nodes("mysql")
    result = {}
    try:
        execute(_docker_init_airflow_mysql, hosts=nodes)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_init_airflow_db():
    DOCKER = "docker"
    DOCKER_IMAGE = AIRFLOW_IMAGE
    DOCKER_TAG = AIRFLOW_TAG
    if AIRFLOW_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = AIRFLOW_GPU_IMAGE
        DOCKER_TAG = AIRFLOW_GPU_TAG
    cmd = "{} run -i -t --name {} ".format(DOCKER, AIRFLOW_NAME)
    cmd += "--network {} ".format(SWARM_NET)
    cmd += "-e AIRFLOW__CORE__SQL_ALCHEMY_CONN={} ".format(AIRFLOW__CORE__SQL_ALCHEMY_CONN)
    cmd += "-v {}:/root/volume ".format(AIRFLOW_VOLUME)
    cmd += "localhost:5000/{}:{} /root/volume/bin/init_airflow.sh ".format(DOCKER_IMAGE, DOCKER_TAG)
    print(cmd)
    run(cmd)

@task
def docker_init_airflow_db():
    env.key_filename = _get_mkey_filename()

    nodes = _get_nodes("airflow")
    result = {}
    _docker_rm(nodes, AIRFLOW_NAME)
    try:
        execute(_docker_init_airflow_db, hosts=nodes)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

@task
def docker_run_airflow():
    nodes = _get_nodes("airflow")
    result = {}
    _docker_rm(nodes, AIRFLOW_NAME)
    DOCKER = "docker"
    DOCKER_IMAGE = AIRFLOW_IMAGE
    DOCKER_TAG = AIRFLOW_TAG
    if JUPYTER_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = AIRFLOW_GPU_IMAGE
        DOCKER_TAG = AIRFLOW_GPU_TAG

    try:
        cmd = "{} run -i -t -d --name {} ".format(DOCKER, AIRFLOW_NAME)
        cmd += "--restart=always --network {} ".format(SWARM_NET)
        cmd += "-p {}:8080 ".format(AIRFLOW_PORT)
	cmd += "-v {}:/root/mnt/dfs ".format(SKP_DFS)
        cmd += "-v {}:/root/volume ".format(AIRFLOW_VOLUME)
        cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(SSHFS_ID, SSHFS_HOST, SSHFS_VOLUME)
        cmd += "-e S3_ACCOUNT={} ".format(S3_ACCOUNT)
        cmd += "-e AIRFLOW__CORE__SQL_ALCHEMY_CONN={} ".format(AIRFLOW__CORE__SQL_ALCHEMY_CONN)
        cmd += "localhost:5000/{}:{} /root/volume/bin/run_airflow.sh ".format(DOCKER_IMAGE, DOCKER_TAG)
        print(cmd)
        _docker_run(nodes, cmd)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_init_airflow_web_passwd():
    cmd = "docker exec -it {} python /root/volume/var/airflow/airflow_init_web_passwd.py".format(AIRFLOW_NAME)
    print(cmd)
    return run(cmd)

@task
def docker_init_airflow_web_passwd():
    env.key_filename = _get_mkey_filename()

    nodes = _get_nodes("airflow")
    result = {}
    try:
        execute(_docker_init_airflow_web_passwd, hosts=nodes)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_run_portainer(PORTAINER_ADMIN_PW):
    cmd = "docker run -i -t -d --name {} ".format(PORTAINER_NAME)
    cmd += "--privileged --restart=always --network {} ".format(SWARM_NET)
    cmd += "-p {}:9000 ".format(PORTAINER_PORT)
    cmd += "-v /var/run/docker.sock:/var/run/docker.sock portainer/portainer "
    cmd += "--admin-password '{}' ".format(PORTAINER_ADMIN_PW)
    cmd += "-H unix:///var/run/docker.sock "
    print(cmd)
    return run(cmd)

@task
def docker_run_portainer():
    env.key_filename = _get_mkey_filename()

    nodes = _get_nodes("portainer")
    result = {}
    _docker_rm(nodes, PORTAINER_NAME)
    try:
        local("sudo apt-get install -y apache2-utils")
        PORTAINER_ADMIN_PW = local("htpasswd -nb -B {} {} | cut -d ':' -f 2".format(PORTAINER_ID, PORTAINER_PW), capture=True)
        print("PORTAINER_ADMIN_PW: {}".format(PORTAINER_ADMIN_PW))

        execute(_docker_run_portainer, PORTAINER_ADMIN_PW=PORTAINER_ADMIN_PW, hosts=nodes)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_run_zookeeper():
    env.key_filename = _get_mkey_filename()

    path_volume = "{}/{}".format(ZOOKEEPER_VOLUME, env.host)
    _run_mkdir(path_volume)
    cmd = "docker run -i -t -d --name {} ".format(ZOOKEEPER_NAME)
    cmd += "--restart=always --network {} ".format(SWARM_NET)
    cmd += "-p {}:2181 ".format(ZOOKEEPER_PORT)
    cmd += "-v {}:/opt/zookeeper/data ".format(path_volume)
    cmd += "localhost:5000/{}:{} ".format(ZOOKEEPER_IMAGE, ZOOKEEPER_TAG)
    print(cmd)
    return run(cmd)

@task
def docker_run_zookeeper():
    nodes = _get_nodes("zookeeper")
    result = {}
    _docker_rm(nodes, ZOOKEEPER_NAME)
    try:
        execute(_docker_run_zookeeper, hosts=nodes)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_run_kafka():
    env.key_filename = _get_mkey_filename()

    path_volume = "{}/{}".format(KAFKA_VOLUME, env.host)
    _run_mkdir(path_volume)
    cmd = "docker run -i -t -d --name {} ".format(KAFKA_NAME)
    cmd += "--restart=always --network {} ".format(SWARM_NET)
    cmd += "-p {}:9094 -p {}:9092 ".format(KAFKA_ADVERTISED_PORT, KAFKA_PORT)
    cmd += '-e HOSTNAME_COMMAND="{}" '.format("docker info | grep ^Name: | cut -d' ' -f 2")
    cmd += '-e KAFKA_ZOOKEEPER_CONNECT="{}:{}" '.format(ZOOKEEPER_NAME, ZOOKEEPER_PORT)
    cmd += '-e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT" '
    cmd += '-e KAFKA_ADVERTISED_PROTOCOL_NAME="OUTSIDE" '
    cmd += '-e KAFKA_ADVERTISED_PORT="{}" '.format(KAFKA_ADVERTISED_PORT)
    cmd += '-e KAFKA_PROTOCOL_NAME="INSIDE" '
    cmd += '-e KAFKA_PORT="{}" '.format(KAFKA_PORT)
    cmd += "-v {}:/kafka ".format(path_volume)
    cmd += "-v /var/run/docker.sock:/var/run/docker.sock "
    cmd += "localhost:5000/{}:{} ".format(KAFKA_IMAGE, KAFKA_TAG)
    print(cmd)
    return run(cmd)

@task
def docker_run_kafka():
    nodes = _get_nodes("kafka")
    result = {}
    _docker_rm(nodes, KAFKA_NAME)
    try:
        execute(_docker_run_kafka, hosts=nodes)
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

def _docker_run_flask(NAME, PORT, ):
    cmd = "docker run -i -t -d --name {} ".format(NAME)
    cmd += "--privileged --restart=always --network {} ".format(SWARM_NET)
    cmd += "-p {}:5000 ".format(PORT)
    cmd += "-v {}:/root/mnt/dfs ".format(SKP_DFS)
    cmd += "-v {}:/root/volume ".format(FLASK_VOLUME)
    cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(SSHFS_ID, SSHFS_HOST, SSHFS_VOLUME)
    cmd += "-e S3_ACCOUNT={} ".format(S3_ACCOUNT)
    cmd += "-e MYSQL_ROOT_PASSWORD={} ".format(MYSQL_ROOT_PASSWORD)
    cmd += "localhost:5000/{}:{} /root/volume/bin/run_jupyter.sh".format(DOCKER_IMAGE, DOCKER_TAG)
    print(cmd)
    return run(cmd)

@task
def docker_run_flask():
    env.key_filename = _get_mkey_filename()

    nodes = _get_nodes("flask")
    result = {}
    _docker_rm(nodes, env.NAME)

    DOCKER = "docker"
    DOCKER_IMAGE = FLASK_IMAGE
    DOCKER_TAG = FLASK_TAG
    if FLASK_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = FLASK_GPU_IMAGE
        DOCKER_TAG = FLASK_GPU_TAG

    try:
        cmd = "{} run -i -t -d --name {} ".format(DOCKER, env.NAME)
        cmd += "--privileged --restart=always --network {} ".format(SWARM_NET)
        cmd += "-p {}:5000 ".format(env.PORT)
        cmd += "-v {}:/root/mnt/dfs ".format(SKP_DFS)
        cmd += "-v {}:/root/volume ".format(FLASK_VOLUME)
        cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(SSHFS_ID, SSHFS_HOST, SSHFS_VOLUME)
        cmd += "-e S3_ACCOUNT={} ".format(S3_ACCOUNT)
        cmd += "-e MYSQL_ROOT_PASSWORD={} ".format(MYSQL_ROOT_PASSWORD)
        cmd += "-e FLASK_SECRET={} ".format(FLASK_SECRET)
        cmd += "localhost:5000/{}:{} {}/bin/run_flask.sh".format(DOCKER_IMAGE, DOCKER_TAG, env.VOLUME)
        print(cmd)
        _docker_run(nodes, cmd)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result

@task
def docker_run_nginx():
    env.key_filename = _get_mkey_filename()

    nodes = _get_nodes("nginx")
    result = {}
    _docker_rm(nodes, env.NAME)

    DOCKER = "docker"
    DOCKER_IMAGE = NGINX_IMAGE
    DOCKER_TAG = NGINX_TAG

    try:
        cmd = "{} run -i -t -d --name {} ".format(DOCKER, env.NAME)
        cmd += "--privileged --restart=always --network {} ".format(SWARM_NET)
        cmd += "-p {}:80 ".format(env.PORT)
        cmd += "-v {}:/root/mnt/dfs ".format(SKP_DFS)
        cmd += "-v {}:/root/volume ".format(NGINX_VOLUME)
        cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(SSHFS_ID, SSHFS_HOST, SSHFS_VOLUME)
        cmd += "-e S3_ACCOUNT={} ".format(S3_ACCOUNT)
        cmd += "localhost:5000/{}:{} {}/bin/run_nginx.sh".format(DOCKER_IMAGE, DOCKER_TAG, env.VOLUME)
        print(cmd)
        _docker_run(nodes, cmd)
        result["status"] = "SUCCESS"
    except BaseException as e:
        result["message"] = e
        result["status"] = "FAIL"

    print(result)
    return result
