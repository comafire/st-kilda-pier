from __future__ import with_statement
from invoke import task
import os, sys, re
import env, utils

# DOCKER
@task
def install(c):
    uname = utils.run_with_exit(c, "uname")
    print("uname: {}".format(uname))

    cmds = [
        "sudo apt-get update",
        "sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common",
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -",
        '\'sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"\'',
        "sudo apt-get update",
        "sudo apt-get install -y docker-ce",
        "sudo usermod -aG docker $USER"
    ]
    for hk, hv in env.hosts.iteritems():
        for cmd in cmds:
            rcmd = "ssh -o StrictHostKeyChecking=no {}@{} {}".format(env.SKP_USER, hv["ipv4"], cmd)
            utils.run_with_exit(c, rcmd)

# DOCKER-MACHINE
@task
def machine_install(c):
    uname = utils.run_with_exit(c, "uname")
    print("uname: {}".format(uname))

    # reference: https://docs.docker.com/machine/install-machine/#install-bash-completion-scripts
    cmd = "curl -L https://github.com/docker/machine/releases/download/v0.14.0/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine && sudo install /tmp/docker-machine /usr/local/bin/docker-machine"
    utils.run_with_exit(c, cmd)

    if uname.find('Linux') > -1:
        cmd = "sudo usermod -aG docker $USER"
        utils.run_with_exit(c, cmd)

@task
def machine_create(c):
    ports = [22, 2376, 2377, 7946, 4789]

    for k, v in env.hosts.iteritems():
        for port in ports:
            cmd = "ssh -o StrictHostKeyChecking=no {}@{} sudo ufw allow {}".format(env.SKP_USER, v["ipv4"], port)
            utils.run_with_exit(c, cmd)

        cmd = "docker-machine create --driver generic --generic-ip-address {} --generic-ssh-key $HOME/.ssh/id_rsa --generic-ssh-user {} {}".format(v["ipv4"], env.SKP_USER, k)
        utils.run_with_exit(c, cmd)

        cmd = "ssh -o StrictHostKeyChecking=no {}@{} sudo usermod -aG docker {}".format(env.SKP_USER, v["ipv4"], env.SKP_USER)
        utils.run_with_exit(c, cmd)

@task
def machine_ls(c):
    cmd = "docker-machine ls"
    utils.run_with_exit(c, cmd)

@task
def machine_rm(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine rm -f {}".format(k)
        utils.run_with_exit(c, cmd)

# DOCKER-SWARM
@task
def swarm_init(c):
    mk, mv = utils.get_master(env.hosts)
    SKP_MIP = mv['ipv4']
    cmd = "docker swarm init --advertise-addr {}".format(SKP_MIP)
    utils.run_with_exit(c, cmd)

@task
def swarm_leave(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker swarm leave --force"
        rcmd = "docker-machine ssh {} {}".format(k, cmd)
        utils.run_without_exit(c, rcmd)

@task
def swarm_join(c):
    managers = {}
    workers = {}
    for k, v in env.hosts.iteritems():
        #print(k, v)
        if "manager" in v["roles"]:
            if "master" not in v["roles"]:
                managers[k] = v
        if "worker" in v["roles"]:
            workers[k] = v

    print("managers: %s" % managers)
    print("workers: %s" % workers)

    mk, mv = utils.get_master(env.hosts)
    cmd = "docker-machine ssh {} docker swarm join-token manager".format(mk)
    res = c.run(cmd)
    cmd_manager = re.search(r'docker\sswarm\sjoin.*:[0-9]{4}', res.stdout.strip(), re.DOTALL).group()
    cmd_manager = re.sub(r'[\\\r\n]', "", cmd_manager)
    cmd = "docker-machine ssh {} docker swarm join-token worker".format(mk)
    res = c.run(cmd)
    cmd_worker = re.search(r'docker\sswarm\sjoin.*:[0-9]{4}', res.stdout.strip(), re.DOTALL).group()
    cmd_worker = re.sub(r'[\\\r\n]', "", cmd_worker)

    for k, v in managers.iteritems():
        cmd = "docker-machine ssh {} {}".format(k, cmd_manager)
        utils.run_with_exit(c, cmd)

    for k, v in workers.iteritems():
        cmd = "docker-machine ssh {} {}".format(k, cmd_worker)
        utils.run_with_exit(c, cmd)

@task
def swarm_label(c):
    labels = {}
    for k, v in env.hosts.iteritems():
        #print(k, v)
        labels[k] = ""
        for lk, lv in v["labels"].iteritems():
            labels[k] += " --label-add %s=%s " % (lk, lv)

    for k, v in labels.iteritems():
        cmd = "docker node update {} {}".format(v, k)
        utils.run_with_exit(c, cmd)

# DOCKER
@task
def node_ls(c):
    cmd = "docker node ls"
    utils.run_with_exit(c, cmd)

@task
def network_create(c, name=""):
    networks = utils.get_networks(env.networks, name)
    for nk, nv in networks.iteritems():
        opts = " ".join(nv["opts"])
        cmd = "docker network create {} {}".format(opts, nk)
        utils.run_with_exit(c, cmd)

@task
def network_rm(c, name=""):
    networks = utils.get_networks(env.networks, name)
    for nk, nv in networks.iteritems():
        cmd = "docker network rm {}".format(nk)
        utils.run_with_exit(c, cmd)

@task
def network_ls(c):
    cmd = "docker network ls"
    utils.run_with_exit(c, cmd)

@task
def ps(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine ssh {} docker ps".format(k)
        utils.run_with_exit(c, cmd)

@task
def log(c, host, name):
    cmd = 'docker logs -f {}'.format(name)
    rcmd = "docker-machine ssh {} {}".format(host, cmd)
    # rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, host, cmd)
    res = c.run(rcmd, pty=True)

@task
def exec_shell(c, host, name):
    cmd = 'docker exec -it {} /bin/bash'.format(name)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
    res = c.run(rcmd, pty=True)

# DOCKER_VOLUME_PLUGIN
@task
def sshfs_plugin_install(c):
    cmd = "docker plugin install --grant-all-permissions vieux/sshfs sshkey.source=$HOME/.ssh/"
    _docker_ssh_without_exit(c, env.hosts, cmd)

@task
def sshfs_plugin_rm(c):
    cmd = "docker plugin disable vieux/sshfs"
    _docker_ssh_without_exit(c, env.hosts, cmd)
    cmd = "docker plugin rm vieux/sshfs"
    _docker_ssh_without_exit(c, env.hosts, cmd)

@task
def sshfs_copy_id(c, name, passwd):
    cmd = "sshpass -p {} ssh-copy-id -i $HOME/.ssh/id_rsa.pub -o StrictHostKeyChecking=no {}".format(passwd, env.volumes[name]["conn"])
    _docker_ssh(c, env.hosts, cmd)

# DOCKER_VOLUME
def _is_matched_label(hv, vv):
    try:
        vv["labels"]
    except:
        return True

    if not vv["labels"]:
        return True

    for hlk, hlv in hv["labels"].iteritems():
        if hlv != "enable":
            continue
        if hlk in vv["labels"]:
            return True
    return False

@task
def volume_create(c, name=""):
    volumes = utils.get_volumes(env.volumes, name)
    for hk, hv in env.hosts.iteritems():
        for vk, vv in volumes.iteritems():
            if not _is_matched_label(hv, vv):
                continue
            print("type: {}".format(vv["type"]))
            opts = os.path.expandvars(" ".join(vv["opts"]))
            if vv["type"] == "nfs":
                cmds = [
                    "docker volume create --name {} {} ".format(vk, opts)
                ]
            elif vv["type"] == "sshfs":
                cmds = [
                    "docker volume create -d vieux/sshfs --name {} {} ".format(vk, opts)
                ]
            elif vv["type"] == "blobfs":
                config_file = "$HOME/tmp/volumes/{}/blob-passwd".format(vk)
                tmp_path = "$HOME/tmp/volumes/{}/blobfusetmp".format(vk)
                cmds = [
                    "mkdir -p $HOME/tmp/volumes/{}".format(vk),
                    "rm -rf {}".format(config_file),
                    "\"echo 'accountName {}' >> {}\"".format(vv["account_name"], config_file),
                    "\"echo 'accountKey {}' >> {}\"".format(vv["account_key"], config_file),
                    "\"echo 'containerName {}' >> {}\"".format(vv["container_name"], config_file),
                    "chmod 600 {}".format(config_file),
                    "mkdir -p {}".format(os.path.expandvars(vv["path"])),
                    "mkdir -p {}".format(tmp_path),
                    "sudo blobfuse {} --tmp-path={} -o attr_timeout=240 -o entry_timeout=240 -o negative_timeout=120 --config-file={}".format(os.path.expandvars(vv["path"]), tmp_path, config_file),
                    "docker volume create --name {} {} ".format(vk, opts)
                ]
            elif vv["type"] == "s3fs":
                config_file = "$HOME/tmp/volumes/{}/s3-passwd".format(vk)
                cmds = [
                    "mkdir -p $HOME/tmp/volumes/{}".format(vk),
                    "rm -rf {}".format(config_file),
                    "\"echo '{}:{}' >> {}\"".format(vv["account_id"], vv["account_key"], config_file),
                    "chmod 600 {}".format(config_file),
                    "mkdir -p {}".format(os.path.expandvars(vv["path"])),
                    "sudo s3fs {} {} -o passwd_file={}".format(vv["bucket"], os.path.expandvars(vv["path"]), config_file),
                    "docker volume create --name {} {} ".format(vk, opts)
                ]
            elif vv["type"] == "fs":
                cmds = [
                    "mkdir -p {}".format(os.path.expandvars(vv["path"])),
                    "docker volume create --name {} {} ".format(vk, opts)
                ]
            else:
                print("Unknown Volume Type: {}".format(vv["type"]))
                sys.exit(-1)
            for cmd in cmds:
                rcmd = "docker-machine ssh {} {}".format(hk, cmd)
                utils.run_with_exit(c, rcmd)

@task
def volume_ls(c, name=""):
    volumes = utils.get_volumes(env.volumes, name)
    for hk, hv in env.hosts.iteritems():
        cmd = "docker volume ls"
        rcmd = "docker-machine ssh {} {}".format(hk, cmd)
        utils.run_without_exit(c, rcmd)

@task
def volume_rm(c, name=""):
    volumes = utils.get_volumes(env.volumes, name)
    for hk, hv in env.hosts.iteritems():
        for vk, vv in volumes.iteritems():
            if not _is_matched_label(hv, vv):
                continue
            if vv["type"] == "blobfs":
                cmds = [
                    "sudo umount {}".format(os.path.expandvars(vv["path"])),
                    "docker volume rm -f {} ".format(vk)
                ]
            elif vv["type"] == "s3fs":
                cmds = [
                    "sudo umount {}".format(os.path.expandvars(vv["path"])),
                    "docker volume rm -f {} ".format(vk)
                ]
            else:
                cmds = [
                    "docker volume rm -f {} ".format(vk)
                ]
            for cmd in cmds:
                rcmd = "docker-machine ssh {} {}".format(hk, cmd)
                utils.run_without_exit(c, rcmd)

def _docker_rm(c, hosts, name):
    for k, v in hosts.iteritems():
        cmd = "docker rm -f {} ".format(name)
        rcmd = "docker-machine ssh {} {}".format(k, cmd)
        utils.run_without_exit(c, rcmd)

def _docker_ssh(c, hosts, cmd):
    for k, v in hosts.iteritems():
        rcmd = "docker-machine ssh {} {}".format(k, cmd)
        utils.run_with_exit(c, rcmd)

def _docker_ssh_without_exit(c, hosts, cmd):
    for k, v in hosts.iteritems():
        rcmd = "docker-machine ssh {} {}".format(k, cmd)
        utils.run_without_exit(c, rcmd)

def _get_opts(cv):
    cmd = ""
    try:
        if len(cv["networks"]) > 0:
            cmd += "--network {} ".format(" --network ".join(cv["networks"]))
    except:
        pass
    try:
        if len(cv["ports"]) > 0:
            cmd += "-p {} ".format(" -p ".join(cv["ports"]))
    except:
        pass
    try:
        if len(cv["volumes"]) > 0:
            cmd += "-v {} ".format(os.path.expandvars(" -v ".join(cv["volumes"])))
    except:
        pass
    try:
        if len(cv["environments"]) > 0:
            cmd += "-e {} ".format(os.path.expandvars(" -e ".join(cv["environments"])))
    except:
        pass
    return cmd

@task
def run(c, name):
    sk, sv = utils.get_service(env.services, name)
    hosts = utils.get_hosts(env.hosts, sv["label"])
    cmd = ""
    if sv["label"] == "registry":
        _docker_rm(c, hosts, sk)
        cmd = "docker run -i -t -d --privileged --restart=always --name {} ".format(sk)
        cmd += _get_opts(sv)
        cmd += "{}".format(sv["image"])
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "jupyter":
        _docker_rm(c, hosts, sk)
        cmd = "{} run -i -t -d --privileged --restart=always --name {} ".format(sv["docker"], sk)
        cmd += _get_opts(sv)
        cmd += "{} {}".format(sv["image"], os.path.expandvars(sv["cmd"]))
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "spark-master":
        _docker_rm(c, hosts, sk)
        cmd = "{} run -i -t -d --privileged --restart=always --name {} ".format(sv["docker"], sk)
        cmd += _get_opts(sv)
        cmd += "{} {}".format(sv["image"], os.path.expandvars(sv["cmd"]))
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "spark-worker":
        _docker_rm(c, hosts, sk)
        cmd = "{} run -i -t -d --privileged --restart=always --name {} ".format(sv["docker"], sk)
        cmd += _get_opts(sv)
        cmd += "{} {}".format(sv["image"], os.path.expandvars(sv["cmd"]))
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "mysql":
        _docker_rm(c, hosts, sk)
        cmd = "docker run -i -t -d --privileged --restart=always --name {} ".format(sk)
        cmd += _get_opts(sv)
        cmd += "{} --default-authentication-plugin=mysql_native_password ".format(sv["image"])
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "pgsql":
        _docker_rm(c, hosts, sk)
        cmd = "docker run -i -t -d --privileged --restart=always --name {} ".format(sk)
        cmd += _get_opts(sv)
        cmd += "{} ".format(sv["image"])
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "airflow":
        _docker_rm(c, hosts, sk)
        cmd = "{} run -i -t -d --privileged --restart=always --name {} ".format(sv["docker"], sk)
        cmd += _get_opts(sv)
        cmd += "{} {}".format(sv["image"], os.path.expandvars(sv["cmd"]))
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "portainer":
        _docker_rm(c, hosts, sk)
        cmd = "docker run -i -t -d --privileged --restart=always --name {} ".format(sk)
        cmd += _get_opts(sv)
        cmd += "{} {}".format(sv["image"], os.path.expandvars(sv["cmd"]))
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "portainer-agent":
        _docker_rm(c, hosts, sk)
        cmd = "docker run -i -t -d --privileged --restart=always --name {} ".format(sk)
        cmd += _get_opts(sv)
        cmd += "{}".format(sv["image"])
        _docker_ssh(c, hosts, cmd)
    elif sv["label"] == "zookeeper":
        zid = 0
        for k, v in hosts.iteritems():
            zid += 1
            cmd = "docker rm -f {}-{}".format(sk, zid)
            rcmd = "docker-machine ssh {} {}".format(k, cmd)
            utils.run_without_exit(c, rcmd)

        with open('/tmp/zoo.cfg', 'w') as f:
            lines = ['tickTime=2000', 'dataDir=/opt/zookeeper/data', 'clientPort=2181', 'initLimit=5', 'syncLimit=2']
            zid = 0
            for k, v in hosts.iteritems():
                zid += 1
                lines.append("server.{}={}-{}:2888:3888".format(zid, sk, zid))
            for line in lines:
                f.write("{}\n".format(line))

        zid = 0
        for k, v in hosts.iteritems():
            zid += 1

            with open('/tmp/myid', 'w') as f:
                f.write("{}\n".format(zid))

            path_z = os.path.expandvars(sv["path"])
            path_conf = "{}/conf".format(path_z)
            cmd = "sudo mkdir -p {} ".format(path_conf)
            rcmd = "docker-machine ssh {} {}".format(k, cmd)
            utils.run_without_exit(c, rcmd)

            path_data = "{}/data".format(path_z)
            cmd = "sudo mkdir -p {} ".format(path_data)
            rcmd = "docker-machine ssh {} {}".format(k, cmd)
            utils.run_without_exit(c, rcmd)

            cmd = "docker-machine scp /tmp/zoo.cfg {}:/tmp/zoo.cfg ".format(k)
            utils.run_with_exit(c, cmd)
            cmd = "docker-machine ssh {} sudo cp /tmp/zoo.cfg {} ".format(k, path_conf)
            utils.run_with_exit(c, cmd)

            cmd = "docker-machine scp /tmp/myid {}:/tmp/myid ".format(k)
            utils.run_with_exit(c, cmd)
            cmd = "docker-machine ssh {} sudo cp /tmp/myid {} ".format(k, path_data)
            utils.run_with_exit(c, cmd)

            cmd = "docker run -i -t -d --privileged --restart=always --name {}-{} ".format(sk, zid)
            cmd += _get_opts(sv)
            cmd += "{}".format(sv["image"])
            rcmd = "docker-machine ssh {} {}".format(k, cmd)
            utils.run_without_exit(c, rcmd)
    elif sv["label"] == "kafka":
        _docker_rm(c, hosts, sk)

        zsk, zsv = utils.get_service(env.services, sv["zookeeper"])
        zhosts = utils.get_hosts(env.hosts, "zookeeper")
        zid = 0
        zconns = []
        for zk, zv in zhosts.iteritems():
            zid += 1
            zconns.append("{}-{}:2181".format(zsk, zid))
        zconn = ",".join(zconns)
        print("Zookeeper Conn: {}".format(zconn))

        bid = 0
        for k, v in hosts.iteritems():
            bid += 1

            cmd = "docker-machine ip {} ".format(k)
            res = c.run(cmd)
            ip = res.stdout.strip()

            cmd = "docker run -i -t -d --privileged --restart=always --name {} ".format(sk)
            cmd += _get_opts(sv)
            cmd += '-e KAFKA_BROKER_ID="{}" '.format(bid)
            cmd += '-e KAFKA_ADVERTISED_HOST_NAME="{}" '.format(k)
            cmd += '-e KAFKA_ZOOKEEPER_CONNECT="{}" '.format(zconn)
            cmd += '-e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT" '
            cmd += '-e KAFKA_ADVERTISED_LISTENERS="INSIDE://:9092,OUTSIDE://{}:9094" '.format(k)
            cmd += '-e KAFKA_LISTENERS="INSIDE://:9092,OUTSIDE://:9094" '
            cmd += '-e KAFKA_INTER_BROKER_LISTENER_NAME="INSIDE" '
            cmd += '-e KAFKA_ADVERTISED_PORT="9092" '
            cmd += "{}".format(sv["image"])
            rcmd = "docker-machine ssh {} {}".format(k, cmd)
            utils.run_with_exit(c, rcmd)
    else:
        print("Unkown Label: {}".format(cv["label"]))
        sys.exit(-1)

@task
def rm(c, name):
    sk, sv = utils.get_service(env.services, name)
    hosts = utils.get_hosts(env.hosts, sv["label"])
    if sv["label"] == "zookeeper":
        zid = 0
        for k, v in hosts.iteritems():
            zid += 1
            cmd = "docker rm -f {}-{}".format(sk, zid)
            rcmd = "docker-machine ssh {} {}".format(k, cmd)
            utils.run_without_exit(c, rcmd)
    else:
        _docker_rm(c, hosts, sk)

# DOCKER IMAGE
@task
def image_build(c, name=""):
    images = utils.get_images(env.images, name)
    for ik, iv in images.iteritems():
        cmd = "docker build "
        cmd += " ".join(iv["opts"])
        cmd += " {}/etc/docker-file/{} --tag {}:{} ".format(env.SKP_HOME, iv["path"], iv["image"], iv["tag"])
        utils.run_with_exit(c, cmd)

        cmd = "docker image tag {}:{} {}/{}:{}".format(iv["image"], iv["tag"], iv["registry"], iv["image"], iv["tag"])
        utils.run_with_exit(c, cmd)
        cmd = "docker push {}/{}:{}".format(iv["registry"], iv["image"], iv["tag"])
        utils.run_with_exit(c, cmd)

@task
def image_list(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine ssh {} docker images".format(k)
        utils.run_with_exit(c, cmd)

@task
def image_rm(c, image, tag):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine ssh {} docker image rm -f {}:{}".format(k, image, tag)
        utils.run_with_exit(c, cmd)

@task
def image_prune(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine ssh {} docker image prune ".format(k)
        utils.run_with_exit(c, cmd)

# MYSQL
@task
def mysql_client(c, host, name):
    ck, cv = utils.get_service(env.services, name)
    passwd = ""
    for e in cv["environments"]:
        if e.find("MYSQL_ROOT_PASSWORD") > -1:
            passwd = e.split("=")[1]

    cmd = 'docker exec -it {} mysql -uroot -p"{}"'.format(name, passwd)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
    res = c.run(rcmd, pty=True)

@task
def mysql_create_airflow_db(c, host, name):
    mysql_name = name.split(":")[0]
    airflow_name = name.split(":")[1]
    ck, cv = utils.get_service(env.services, airflow_name)
    db = ""
    db_user = ""
    db_pw = ""
    for e in cv["environments"]:
        if e.replace(" ", "").find("AIRFLOW_DB=") > -1:
            db = e.split("=")[1]
        if e.replace(" ", "").find("AIRFLOW_DB_USER=") > -1:
            db_user = e.split("=")[1]
        if e.replace(" ", "").find("AIRFLOW_DB_PASSWORD=") > -1:
            db_pw = e.split("=")[1]

    ck, cv = utils.get_service(env.services, mysql_name)
    mysql_pw = ""
    for e in cv["environments"]:
        if e.find("MYSQL_ROOT_PASSWORD") > -1:
            mysql_pw = e.split("=")[1]

    queries = []
    queries.append("DROP DATABASE IF EXISTS {};".format(db))
    queries.append("DROP USER IF EXISTS {};".format(db_user))
    queries.append("CREATE DATABASE {};".format(db))
    queries.append("CREATE USER IF NOT EXISTS '{}'@'%' IDENTIFIED BY '{}';".format(db_user, db_pw))
    queries.append("GRANT ALL PRIVILEGES ON {}.* TO '{}'@'%';".format(db, db_user))
    queries.append("FLUSH PRIVILEGES;")

    for query in queries:
        sql_cmd = 'mysql -uroot -p\\"{}\\" -e\\"{}\\"'.format(mysql_pw, query)
        cmd = 'docker exec -it {} "{}"'.format(mysql_name, sql_cmd)
        rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
        res = c.run(rcmd, pty=True)

# PGSQL
@task
def pgsql_client(c, host, name):
    ck, cv = utils.get_service(env.services, name)
    passwd = ""
    for e in cv["environments"]:
        if e.find("PGSQL_ROOT_PASSWORD") > -1:
            passwd = e.split("=")[1]

    cmd = "docker exec -it {} \"/bin/bash -c 'PGPASSWORD={} psql -U postgres'\"".format(name, passwd)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
    res = c.run(rcmd, pty=True)

@task
def pgsql_create_airflow_db(c, host, name):
    pgsql_name = name.split(":")[0]
    airflow_name = name.split(":")[1]
    ck, cv = utils.get_service(env.services, airflow_name)
    db = ""
    db_user = ""
    db_pw = ""
    for e in cv["environments"]:
        if e.replace(" ", "").find("AIRFLOW_DB=") > -1:
            db = e.split("=")[1]
        if e.replace(" ", "").find("AIRFLOW_DB_USER=") > -1:
            db_user = e.split("=")[1]
        if e.replace(" ", "").find("AIRFLOW_DB_PASSWORD=") > -1:
            db_pw = e.split("=")[1]

    ck, cv = utils.get_service(env.services, pgsql_name)
    pgsql_pw = ""
    for e in cv["environments"]:
        if e.find("PGSQL_ROOT_PASSWORD") > -1:
            pgsql_pw = e.split("=")[1]

    queries = []
    queries.append("DROP DATABASE IF EXISTS {};".format(db))
    queries.append("DROP USER IF EXISTS {};".format(db_user))
    queries.append("CREATE DATABASE {};".format(db))
    queries.append("CREATE USER {} PASSWORD '{}';".format(db_user, db_pw))
    queries.append("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {};".format(db, db_user))

    for query in queries:
        sql_cmd = 'psql -U postgres -c\\"{}\\"'.format(query)
        cmd = 'docker exec -it {} "{}"'.format(pgsql_name, sql_cmd)
        rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
        res = c.run(rcmd, pty=True)

# AIRFLOW
@task
def airflow_init_db(c, host, name):
    ck, cv = utils.get_service(env.services, name)
    cmd = "docker rm -f {} ".format(name)
    rcmd = "docker-machine ssh {} {}".format(host, cmd)
    utils.run_without_exit(c, rcmd)

    cmd = "{} run -i -t -d --privileged --restart=always --name {} ".format(cv["docker"], ck)
    cmd += "--network {} ".format(" --network ".join(cv["networks"]))
    cmd += "-p {} ".format(" -p ".join(cv["ports"]))
    cmd += "-v {} ".format(os.path.expandvars(" -v ".join(cv["volumes"])))
    cmd += "-e {} ".format(os.path.expandvars(" -e ".join(cv["environments"])))
    cmd += "{} {}".format(cv["image"], os.path.expandvars("$SKP_SHOME/volume/bin/init_airflow.sh"))
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
    res = c.run(rcmd, pty=True)

@task
def airflow_init_web_passwd(c, host, name):
    ck, cv = utils.get_service(env.services, name)
    cmd = "docker exec -it {} python {}".format(name, os.path.expandvars("$SKP_SHOME/volume/var/airflow/airflow_init_web_passwd.py"))
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, env.hosts[host]["ipv4"], cmd)
    res = c.run(rcmd, pty=True)
