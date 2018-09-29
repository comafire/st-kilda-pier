from __future__ import with_statement
from invoke import task
import os, sys, re
import env, utils

def _docker_rm(c, nodes, name):
    for node in nodes:
        rcmd = "docker-machine ssh {} ".format(node)
        rcmd += "docker rm -f {} ".format(name)
        try:
            c.run(rcmd)
        except:
            continue

def _docker_ssh(c, nodes, cmd):
    for node in nodes:
        rcmd = "docker-machine ssh {} ".format(node)
        rcmd += cmd
        utils.run_with_exit(c, rcmd)

@task
def machine_install(c):
    # reference: https://docs.docker.com/machine/install-machine/#install-bash-completion-scripts
    cmd = "curl -L https://github.com/docker/machine/releases/download/v0.14.0/docker-machine-$(uname -s)-$(uname -m) >/tmp/docker-machine && sudo install /tmp/docker-machine /usr/local/bin/docker-machine"
    utils.run_with_exit(c, cmd)

    cmd = "sudo usermod -aG docker {}".format(env.SKP_USER)
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
def machine_rm(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine rm -f {}".format(k)
        utils.run_with_exit(c, cmd)

@task
def swarm_init(c):
    SKP_MNAME, SKP_MIP = utils.get_mhost(env.hosts)
    cmd = "docker swarm init --advertise-addr {}".format(SKP_MIP)
    utils.run_with_exit(c, cmd)

@task
def swarm_join(c):
    managers = []
    workers = []
    for k, v in env.hosts.iteritems():
        #print(k, v)
        if ("manager" in v["groups"]):
            if ("master" not in v["groups"]):
                managers.append(v["ipv4"])
        if ("worker" in v["groups"]):
            workers.append(v["ipv4"])

    print("managers: %s" % managers)
    print("workers: %s" % workers)

    cmd = "docker swarm join-token manager"
    res = c.run(cmd)
    cmd_manager = re.search(r'docker\sswarm\sjoin.*:[0-9]{4}', res.stdout.strip(), re.DOTALL).group()
    cmd_manager = re.sub(r'[\\\r\n]', "", cmd_manager)
    cmd = "docker swarm join-token worker"
    res = c.run(cmd)
    cmd_worker = re.search(r'docker\sswarm\sjoin.*:[0-9]{4}', res.stdout.strip(), re.DOTALL).group()
    cmd_worker = re.sub(r'[\\\r\n]', "", cmd_worker)

    for manager in managers:
        cmd = "ssh -o StrictHostKeyChecking=no {}@{} {}".format(env.SKP_USER, manager, cmd_manager)
        utils.run_with_exit(c, cmd)

    for worker in workers:
        cmd = "ssh -o StrictHostKeyChecking=no {}@{} {}".format(env.SKP_USER, worker, cmd_worker)
        utils.run_with_exit(c, cmd)

@task
def swarm_label(c):
    labels = {}
    for k, v in env.hosts.iteritems():
        #print(k, v)
        labels[k] = ""
        for label in v["labels"]:
            for lk, lv in label.iteritems():
                labels[k] += " --label-add %s=%s " % (lk, lv)

    for k, v in labels.iteritems():
        cmd = "docker node update {} {}".format(v, k)
        utils.run_with_exit(c, cmd)

@task
def swarm_network(c):
    cmd = "docker network create --driver overlay --attachable {}".format(env.SKP_NET)
    utils.run_with_exit(c, cmd)

@task
def ps(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine ssh {} docker ps".format(k)
        utils.run_with_exit(c, cmd)

@task
def exec_shell(c, host, name):
    cmd = 'docker exec -it {} /bin/bash'.format(name)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, host, cmd)
    res = c.run(rcmd, pty=True)

@task
def registry_run(c):
    nodes = utils.get_nodes(env.hosts, "registry")
    utils.run_mkdir(c, env.REGISTRY_VOLUME)
    _docker_rm(c, nodes, env.REGISTRY_NAME)

    cmd = "docker run -i -t -d --name {} ".format(env.REGISTRY_NAME)
    cmd += "--restart=always --network {} ".format(env.SKP_NET)
    cmd += "-p 5000:5000 "
    cmd += "-v {}:/var/lib/registry ".format(env.REGISTRY_VOLUME)
    cmd += "{}:{}".format(env.REGISTRY_IMAGE, env.REGISTRY_TAG)
    _docker_ssh(c, nodes, cmd)

@task
def registry_rm(c):
    nodes = utils.get_nodes(env.hosts, "registry")
    _docker_rm(c, nodes, env.REGISTRY_NAME)

def _image_build_tag_push(c, image, tag):
    cmd = "docker image tag {}:{} localhost:5000/{}:{}".format(image, tag, image, tag)
    utils.run_with_exit(c, cmd)
    cmd = "docker push localhost:5000/{}:{}".format(image, tag)
    utils.run_with_exit(c, cmd)

@task
def image_build_ds(c, locale, gpu, tag):
    image = "skp/docker-ds"
    if gpu == "TRUE":
        image = "{}-gpu".format(image)

    cmd = "docker build --build-arg locale={} --build-arg gpu={} ".format(locale, gpu)
    cmd += "{}/etc/docker-file/skp/docker-ds --tag {}:{} ".format(env.SKP_HOME, image, tag)
    utils.run_with_exit(c, cmd)
    _image_build_tag_push(c, image, tag)

@task
def image_build_zookeeper(c, tag):
    image = "skp/docker-zookeeper"
    cmd = "docker build {}/etc/docker-file/{} --tag {}:{} ".format(env.SKP_HOME, image, image, tag)
    utils.run_with_exit(c, cmd)
    _image_build_tag_push(c, image, tag)

@task
def image_build_kafka(c, tag):
    image = "skp/docker-kafka"
    cmd = "docker build {}/etc/docker-file/{} --tag {}:{} ".format(env.SKP_HOME, image, image, tag)
    utils.run_with_exit(c, cmd)
    _image_build_tag_push(c, image, tag)

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

    # cmd = "curl https://raw.githubusercontent.com/burnettk/delete-docker-registry-image/master/delete_docker_registry_image.py | sudo tee /usr/local/bin/delete_docker_registry_image >/dev/null"
    # utils.run_with_exit(c, cmd)
    # cmd = "sudo chmod a+x /usr/local/bin/delete_docker_registry_image"
    # utils.run_with_exit(c, cmd)
    # cmd = "export REGISTRY_DATA_DIR={}/docker/registry/v2;delete_docker_registry_image --image {}:{} --dry-run".format(env.REGISTRY_VOLUME, image, tag)
    # utils.run_with_exit(c, cmd)

@task
def image_prune(c):
    for k, v in env.hosts.iteritems():
        cmd = "docker-machine ssh {} docker image prune ".format(k)
        utils.run_with_exit(c, cmd)

@task
def jupyter_run(c):
    nodes = utils.get_nodes(env.hosts, "jupyter")
    _docker_rm(c, nodes, env.JUPYTER_NAME)
    DOCKER = "docker"
    DOCKER_IMAGE = env.JUPYTER_IMAGE
    DOCKER_TAG = env.JUPYTER_TAG
    if env.JUPYTER_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = env.JUPYTER_GPU_IMAGE
        DOCKER_TAG = env.JUPYTER_GPU_TAG

    cmd = "{} run -i -t -d --name {} ".format(DOCKER, env.JUPYTER_NAME)
    cmd += "--privileged --restart=always --network {} ".format(env.SKP_NET)
    cmd += "-p {}:8888 -p {}:8088 ".format(env.JUPYTER_PORT, env.JUPYTER_RESTAPIPORT)
    cmd += "-v /var/run/docker.sock:/var/run/docker.sock "
    cmd += "-v {}:/root/mnt/dfs ".format(env.SKP_DFS)
    cmd += "-v {}:/root/volume ".format(env.JUPYTER_VOLUME)
    cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(env.SSHFS_ID, env.SSHFS_HOST, env.SSHFS_VOLUME)
    cmd += "-e S3_ACCOUNT={} ".format(env.S3_ACCOUNT)
    cmd += "-e MYSQL_ROOT_PASSWORD={} ".format(env.MYSQL_ROOT_PASSWORD)
    cmd += "-e FLASK_SECRET={} ".format(env.FLASK_SECRET)
    cmd += "-e JUPYTER_BASEURL={} -e JUPYTER_PASSWORD={} ".format(env.JUPYTER_BASEURL, env.JUPYTER_PASSWORD)
    cmd += "localhost:5000/{}:{} /root/volume/bin/run_jupyter.sh".format(DOCKER_IMAGE, DOCKER_TAG)
    _docker_ssh(c, nodes, cmd)

@task
def jupyter_rm(c):
    nodes = utils.get_nodes(env.hosts, "jupyter")
    _docker_rm(c, nodes, env.JUPYTER_NAME)

@task
def jupyter_shell(c, host):
    cmd = "docker exec -it {} /bin/bash".format(env.JUPYTER_NAME)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, host, cmd)
    res = c.run(rcmd, pty=True)

@task
def spark_run(c):
    master = utils.get_nodes(env.hosts, "spark-master")
    workers = utils.get_nodes(env.hosts, "spark-worker")
    _docker_rm(c, master, env.SPARK_MNAME)
    _docker_rm(c, workers, env.SPARK_WNAME)
    DOCKER = "docker"
    DOCKER_IMAGE = env.SPARK_IMAGE
    DOCKER_TAG = env.SPARK_TAG
    if env.SPARK_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = env.SPARK_GPU_IMAGE
        DOCKER_TAG = env.SPARK_GPU_TAG

    cmd = "{} run -i -t --name {} ".format(DOCKER, env.SPARK_MNAME)
    cmd += "-d --privileged --restart=always --network {} ".format(env.SKP_NET)
    cmd += "-v {}:/root/mnt/dfs ".format(env.SKP_DFS)
    cmd += "-v {}:/root/volume ".format(env.SPARK_VOLUME)
    cmd += "-p {}:8080 ".format(env.SPARK_MPORT)
    cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(env.SSHFS_ID, env.SSHFS_HOST, env.SSHFS_VOLUME)
    cmd += "-e S3_ACCOUNT={} ".format(env.S3_ACCOUNT)
    cmd += "localhost:5000/{}:{} /root/volume/bin/run_spark_master.sh ".format(DOCKER_IMAGE, DOCKER_TAG)
    _docker_ssh(c, master, cmd)

    cmd = "{} run -i -t --name {} ".format(DOCKER, env.SPARK_WNAME)
    cmd += "-d --privileged --restart=always --network {} ".format(env.SKP_NET)
    cmd += "-v {}:/root/mnt/dfs ".format(env.SKP_DFS)
    cmd += "-v {}:/root/volume ".format(env.SPARK_VOLUME)
    cmd += "-e SPARK_URL={} ".format(env.SPARK_URL)
    cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(env.SSHFS_ID, env.SSHFS_HOST, env.SSHFS_VOLUME)
    cmd += "-e S3_ACCOUNT={} ".format(env.S3_ACCOUNT)
    cmd += "localhost:5000/{}:{} /root/volume/bin/run_spark_worker.sh".format(DOCKER_IMAGE, DOCKER_TAG)
    _docker_ssh(c, workers, cmd)

@task
def spark_rm(c):
    master = utils.get_nodes(env.hosts, "spark-master")
    workers = utils.get_nodes(env.hosts, "spark-worker")
    _docker_rm(c, master, env.SPARK_MNAME)
    _docker_rm(c, workers, env.SPARK_WNAME)

@task
def mysql_run(c):
    nodes = utils.get_nodes(env.hosts, "mysql")
    utils.run_mkdir(c, env.MYSQL_VOLUME)
    _docker_rm(c, nodes, env.MYSQL_NAME)
    cmd = "docker run -i -t -d --name {} ".format(env.MYSQL_NAME)
    cmd += "--restart=always --network {} ".format(env.SKP_NET)
    cmd += "-p {}:3306 ".format(env.MYSQL_PORT)
    cmd += "-e MYSQL_ROOT_PASSWORD={} ".format(env.MYSQL_ROOT_PASSWORD)
    cmd += "-e MYSQL_ROOT_HOST=% "
    cmd += "-v {}:/var/lib/mysql ".format(env.MYSQL_VOLUME)
    cmd += "{}:{} --default-authentication-plugin=mysql_native_password ".format(env.MYSQL_IMAGE, env.MYSQL_TAG)
    _docker_ssh(c, nodes, cmd)

@task
def mysql_rm(c):
    nodes = utils.get_nodes(env.hosts, "mysql")
    _docker_rm(c, nodes, env.MYSQL_NAME)

@task
def mysql_client(c, host):
    cmd = 'docker exec -it {} mysql -uroot -p"{}"'.format(env.MYSQL_NAME, env.MYSQL_ROOT_PASSWORD)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, host, cmd)
    res = c.run(rcmd, pty=True)

@task
def mysql_airflow_init(c):
    nodes = utils.get_nodes(env.hosts, "mysql")
    SQL = "DROP DATABASE IF EXISTS {};".format(env.AIRFLOW_DB)
    SQL += "CREATE DATABASE IF NOT EXISTS {};".format(env.AIRFLOW_DB)
    SQL += "CREATE USER IF NOT EXISTS '{}'@'%' IDENTIFIED BY '{}';".format(env.AIRFLOW_DB_USER, env.AIRFLOW_DB_PASSWORD)
    SQL += "GRANT ALL PRIVILEGES ON {}.* TO '{}'@'%';".format(env.AIRFLOW_DB, env.AIRFLOW_DB_USER)
    SQL += "FLUSH PRIVILEGES;"
    mysql_cmd = 'mysql -uroot -p\\"{}\\" -e\\"{}\\"'.format(env.MYSQL_ROOT_PASSWORD, SQL)
    cmd = 'docker exec -it {} "{}"'.format(env.MYSQL_NAME, mysql_cmd)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, nodes[0], cmd)
    res = c.run(rcmd, pty=True)

@task
def airflow_db_init(c):
    nodes = utils.get_nodes(env.hosts, "airflow")
    _docker_rm(c, nodes, env.AIRFLOW_NAME)
    DOCKER = "docker"
    DOCKER_IMAGE = env.AIRFLOW_IMAGE
    DOCKER_TAG = env.AIRFLOW_TAG
    if env.AIRFLOW_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = env.AIRFLOW_GPU_IMAGE
        DOCKER_TAG = env.AIRFLOW_GPU_TAG
    cmd = "{} run -i -t --name {} ".format(DOCKER, env.AIRFLOW_NAME)
    cmd += "--network {} ".format(env.SKP_NET)
    cmd += "-e AIRFLOW__CORE__SQL_ALCHEMY_CONN={} ".format(env.AIRFLOW__CORE__SQL_ALCHEMY_CONN)
    cmd += "-v {}:/root/volume ".format(env.AIRFLOW_VOLUME)
    cmd += "localhost:5000/{}:{} /root/volume/bin/init_airflow.sh ".format(DOCKER_IMAGE, DOCKER_TAG)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, nodes[0], cmd)
    res = c.run(rcmd, pty=True)

@task
def airflow_run(c):
    nodes = utils.get_nodes(env.hosts, "airflow")
    _docker_rm(c, nodes, env.AIRFLOW_NAME)
    DOCKER = "docker"
    DOCKER_IMAGE = env.AIRFLOW_IMAGE
    DOCKER_TAG = env.AIRFLOW_TAG
    if env.AIRFLOW_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = env.AIRFLOW_GPU_IMAGE
        DOCKER_TAG = env.AIRFLOW_GPU_TAG
    cmd = "{} run -i -t --name {} ".format(DOCKER, env.AIRFLOW_NAME)
    cmd += "-d --privileged --restart=always --network {} ".format(env.SKP_NET)
    cmd += "-p {}:8080 ".format(env.AIRFLOW_PORT)
    cmd += "-v {}:/root/mnt/dfs ".format(env.SKP_DFS)
    cmd += "-v {}:/root/volume ".format(env.AIRFLOW_VOLUME)
    cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(env.SSHFS_ID, env.SSHFS_HOST, env.SSHFS_VOLUME)
    cmd += "-e S3_ACCOUNT={} ".format(env.S3_ACCOUNT)
    cmd += "-e AIRFLOW__CORE__SQL_ALCHEMY_CONN={} ".format(env.AIRFLOW__CORE__SQL_ALCHEMY_CONN)
    cmd += "localhost:5000/{}:{} /root/volume/bin/run_airflow.sh ".format(DOCKER_IMAGE, DOCKER_TAG)
    _docker_ssh(c, nodes, cmd)

@task
def airflow_rm(c):
    nodes = utils.get_nodes(env.hosts, "airflow")
    _docker_rm(c, nodes, env.AIRFLOW_NAME)

@task
def airflow_web_passwd_init(c):
    nodes = utils.get_nodes(env.hosts, "airflow")
    cmd = "docker exec -it {} python /root/volume/var/airflow/airflow_init_web_passwd.py".format(env.AIRFLOW_NAME)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, nodes[0], cmd)
    res = c.run(rcmd, pty=True)

@task
def portainer_run(c):
    nodes = utils.get_nodes(env.hosts, "portainer")
    _docker_rm(c, nodes, env.PORTAINER_NAME)
    # # pw setup doesn't support from 1.19.0 over
    # utils.run_with_exit(c, "sudo apt-get install -y apache2-utils")
    # res = c.run("htpasswd -nb -B {} '{}' | cut -d ':' -f 2".format(env.PORTAINER_ID, env.PORTAINER_PW))
    # if res.failed:
    #     return
    # PORTAINER_ADMIN_PW = res.stdout.strip()
    # print("PORTAINER_ADMIN_PW: {}".format(PORTAINER_ADMIN_PW))
    cmd = "docker run -i -t -d --name {} ".format(env.PORTAINER_NAME)
    cmd += "--privileged --restart=always --network {} ".format(env.SKP_NET)
    cmd += "-p {}:9000 ".format(env.PORTAINER_PORT)
    cmd += "-v /var/run/docker.sock:/var/run/docker.sock portainer/portainer "
    # cmd += "--admin-password '{}' ".format(PORTAINER_ADMIN_PW)
    cmd += "-H unix:///var/run/docker.sock "
    _docker_ssh(c, nodes, cmd)

@task
def portainer_rm(c):
    nodes = utils.get_nodes(env.hosts, "portainer")
    _docker_rm(c, nodes, env.PORTAINER_NAME)

@task
def zookeeper_run(c):
    nodes = utils.get_nodes(env.hosts, "zookeeper")
    for id, node in enumerate(nodes):
        zid = id + 1
        rcmd = "docker-machine ssh {} ".format(node)
        rcmd += "docker rm -f {}-{} ".format(env.ZOOKEEPER_NAME, zid)
        try:
            c.run(rcmd)
        except:
            continue

    with open('/tmp/zoo.cfg', 'w') as f:
        lines = ['tickTime=2000', 'dataDir=/opt/zookeeper/data', 'clientPort=2181', 'initLimit=5', 'syncLimit=2']
        for id, node in enumerate(nodes):
            zid = id + 1
            lines.append("server.{}={}-{}:2888:3888".format(zid, env.ZOOKEEPER_NAME, zid))
        for line in lines:
            f.write("{}\n".format(line))

    for id, node in enumerate(nodes):
        zid = id + 1
        path_conf = "{}/conf".format(env.ZOOKEEPER_VOLUME)
        cmd = "docker-machine ssh {} ".format(node)
        cmd += "sudo mkdir -p {} ".format(path_conf)
        utils.run_with_exit(c, cmd)

        path_data = "{}/data".format(env.ZOOKEEPER_VOLUME)
        cmd = "docker-machine ssh {} ".format(node)
        cmd += "sudo mkdir -p {} ".format(path_data)
        utils.run_with_exit(c, cmd)

        with open('/tmp/myid', 'w') as f:
            f.write("{}\n".format(zid))

        cmd = "docker-machine scp /tmp/zoo.cfg {}:/tmp/zoo.cfg ".format(node)
        utils.run_with_exit(c, cmd)
        cmd = "docker-machine ssh {} sudo cp /tmp/zoo.cfg {} ".format(node, path_conf)
        utils.run_with_exit(c, cmd)

        cmd = "docker-machine scp /tmp/myid {}:/tmp/myid ".format(node)
        utils.run_with_exit(c, cmd)
        cmd = "docker-machine ssh {} sudo cp /tmp/myid {} ".format(node, path_data)
        utils.run_with_exit(c, cmd)

        cmd = "docker-machine ssh {} ".format(node)
        cmd += "docker run -i -t -d --name {}-{} ".format(env.ZOOKEEPER_NAME, zid)
        cmd += "--restart=always --network {} ".format(env.SKP_NET)
        cmd += "-p 2181:2181 -p 2888:2888 -p 3888:3888 "
        cmd += "-v {}/zoo.cfg:/opt/zookeeper/conf/zoo.cfg ".format(path_conf)
        cmd += "-v {}:/opt/zookeeper/data ".format(path_data)
        cmd += "localhost:5000/{}:{} ".format(env.ZOOKEEPER_IMAGE, env.ZOOKEEPER_TAG)
        utils.run_with_exit(c, cmd)

@task
def zookeeper_rm(c):
    nodes = utils.get_nodes(env.hosts, "zookeeper")
    for id, node in enumerate(nodes):
        zid = id + 1
        rcmd = "docker-machine ssh {} ".format(node)
        rcmd += "docker rm -f {}-{} ".format(env.ZOOKEEPER_NAME, zid)
        try:
            c.run(rcmd)
        except:
            continue

@task
def kafka_run(c):
    znodes = utils.get_nodes(env.hosts, "zookeeper")
    zconns = []
    for id, znode in enumerate(znodes):
        zid = id + 1
        zconns.append("{}-{}:2181".format(env.ZOOKEEPER_NAME, zid))
    zconn = ",".join(zconns)

    nodes = utils.get_nodes(env.hosts, "kafka")
    _docker_rm(c, nodes, env.KAFKA_NAME)
    for id, node in enumerate(nodes):
        bid = id + 1
        path_volume = "{}/{}".format(env.KAFKA_VOLUME, node)
        cmd = "docker-machine ssh {} ".format(node)
        cmd += "sudo mkdir -p {} ".format(path_volume)
        utils.run_with_exit(c, cmd)

        cmd = "docker-machine ip {} ".format(node)
        res = c.run(cmd)
        ip = res.stdout.strip()

        cmd = "docker-machine ssh {} ".format(node)
        cmd += "docker run -i -t -d --name {} ".format(env.KAFKA_NAME)
        cmd += "--restart=always --network {} ".format(env.SKP_NET)
        cmd += "-p 9092:9092 -p 9094:9094 "
        cmd += '-e KAFKA_BROKER_ID="{}" '.format(bid)
        cmd += '-e KAFKA_ADVERTISED_HOST_NAME="{}" '.format(node)
        cmd += '-e KAFKA_ZOOKEEPER_CONNECT="{}" '.format(zconn)
        cmd += '-e KAFKA_LISTENER_SECURITY_PROTOCOL_MAP="INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT" '
        cmd += '-e KAFKA_ADVERTISED_LISTENERS="INSIDE://:9092,OUTSIDE://{}:9094" '.format(node)
        cmd += '-e KAFKA_LISTENERS="INSIDE://:9092,OUTSIDE://:9094" '
        cmd += '-e KAFKA_INTER_BROKER_LISTENER_NAME="INSIDE" '
        cmd += '-e KAFKA_ADVERTISED_PORT="9092" '
        cmd += "-v {}:/kafka ".format(path_volume)
        cmd += "-v /var/run/docker.sock:/var/run/docker.sock "
        cmd += "localhost:5000/{}:{} ".format(env.KAFKA_IMAGE, env.KAFKA_TAG)
        utils.run_with_exit(c, cmd)

@task
def kafka_rm(c):
    nodes = utils.get_nodes(env.hosts, "kafka")
    _docker_rm(c, nodes, env.KAFKA_NAME)

@task
def flask_run(c, name, port, volume):
    nodes = utils.get_nodes(env.hosts, "flask")
    _docker_rm(c, nodes, name)
    DOCKER = "docker"
    DOCKER_IMAGE = env.FLASK_IMAGE
    DOCKER_TAG = env.FLASK_TAG
    ex_volume = os.path.expandvars(volume)
    print("volume: {}, expanded volume: {}".format(volume, ex_volume))
    if env.FLASK_GPU == "TRUE":
        DOCKER = "nvidia-docker"
        DOCKER_IMAGE = env.FLASK_GPU_IMAGE
        DOCKER_TAG = env.FLASK_GPU_TAG
    cmd = "{} run -i -t -d --name {} ".format(DOCKER, name)
    cmd += "--privileged --restart=always --network {} ".format(env.SKP_NET)
    cmd += "-p {}:5000 ".format(port)
    cmd += "-v {}:/root/mnt/dfs ".format(env.SKP_DFS)
    cmd += "-v {}:/root/volume ".format(ex_volume)
    cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(env.SSHFS_ID, env.SSHFS_HOST, env.SSHFS_VOLUME)
    cmd += "-e S3_ACCOUNT={} ".format(env.S3_ACCOUNT)
    cmd += "-e MYSQL_ROOT_PASSWORD={} ".format(env.MYSQL_ROOT_PASSWORD)
    cmd += "-e FLASK_SECRET={} ".format(env.FLASK_SECRET)
    cmd += "localhost:5000/{}:{} /root/volume/bin/run_flask.sh".format(DOCKER_IMAGE, DOCKER_TAG)
    _docker_ssh(c, nodes, cmd)

@task
def flask_rm(c, name):
    nodes = utils.get_nodes(env.hosts, "flask")
    _docker_rm(c, nodes, name)

@task
def flask_shell(c, host, name):
    cmd = "docker exec -it {} /bin/bash".format(name)
    rcmd = "ssh -o StrictHostKeyChecking=no {}@{} -t {}".format(env.SKP_USER, host, cmd)
    res = c.run(rcmd, pty=True)

@task
def nginx_run(c, name, port, volume):
    nodes = utils.get_nodes(env.hosts, "nginx")
    _docker_rm(c, nodes, name)
    DOCKER = "docker"
    DOCKER_IMAGE = env.NGINX_IMAGE
    DOCKER_TAG = env.NGINX_TAG
    ex_volume = os.path.expandvars(volume)
    print("volume: {}, expanded volume: {}".format(volume, ex_volume))
    cmd = "{} run -i -t -d --name {} ".format(DOCKER, name)
    cmd += "--privileged --restart=always --network {} ".format(env.SKP_NET)
    cmd += "-p {}:80 ".format(port)
    cmd += "-v {}:/root/mnt/dfs ".format(env.SKP_DFS)
    cmd += "-v {}:/root/volume ".format(ex_volume)
    cmd += "-e SSHFS_ID={} -e SSHFS_HOST={} -e SSHFS_VOLUME={} ".format(env.SSHFS_ID, env.SSHFS_HOST, env.SSHFS_VOLUME)
    cmd += "-e S3_ACCOUNT={} ".format(env.S3_ACCOUNT)
    cmd += "localhost:5000/{}:{} /root/volume/bin/run_nginx.sh".format(DOCKER_IMAGE, DOCKER_TAG)
    _docker_ssh(c, nodes, cmd)

@task
def nginx_rm(c, name):
    nodes = utils.get_nodes(env.hosts, "nginx")
    _docker_rm(c, nodes, name)
