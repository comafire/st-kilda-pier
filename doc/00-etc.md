SKP 를 구축하기 위해 작성해야 하는 파일은 아래와 같습니다.

* hosts.json: SKP 의 Node 들의 형상을 정의합니다.
* networks.json: SKP 에서 사용할 Docker Swarm Network들을 정의합니다.
* images.json: SKP 에서 사용되는 Docker Image 들을 정의합니다.
* volumes.json: SKP 에서 사용되는 Docker Volume 들을 정의합니다.
* services.json: SKP 에서 사용되는 Docker Service 들을 정의합니다.

# SKP_HOSTS

SKP의 형상 Cluster, Single 에 따라 예제 template 를 제공합니다.

* Cluster: hosts_cluster.json.template
* Single: hosts_single.json.template

자신에게 해당되는 template 을 hosts.json 이름으로 복사하여 알맞게 수정하여 사용합니다.

hosts.json은 name 을 키로 사용하여 ipv4, labels, roles 를 설정합니다.
```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    "labels" : {
      "registry" : "enable",
      "jupyter" : "enable",
      "spark-master" : "enable",
      "portainer" : "enable",
      "airflow" : "enable",
      "mysql" : "enable",
      "pgsql" : "enable",
      "zookeeper" : "enable",
      "kafka" : "enable",
      "flask" : "enable",
      "nginx" : "enable"
    },
    "roles" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    "labels" : {
      "registry" : "enable",
      "spark-worker" : "enable",
      "zookeeper" : "enable",
      "kafka" : "enable"
    },
    "roles" : ["slave", "manager"]
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    "labels" : {
      "registry" : "enable",
      "spark-worker" : "enable",
      "zookeeper" : "enable",
      "kafka" : "enable"
    },
    "roles" : ["slave", "manager"]
  },
  "c04" : {
    "ipv4" : "192.168.0.54",
    "labels" : {
      "registry" : "enable",
      "spark-worker" : "enable",
      "kafka" : "enable"
    },
    "roles" : ["slave", "worker"]
  },
  "c05" : {
    "ipv4" : "192.168.0.55",
    "labels" : {
      "registry" : "enable",
      "spark-worker" : "enable",
      "kafka" : "enable"
    },
    "roles" : ["slave", "worker"]
  }
}
```

roles 는 skp 에서 수행할 역할을 설정합니다.

* master: spark cluster 의 master (한개 노드)
* slave: spark cluster 의 slave (나머지 노드)
* manager: swarm cluster 의 manager (Cluster일 경우, 최소 3개 노드 필요)
* worker: swarm cluster 의 worker (나머지 노드)

labels 는 노드상에서 수행할 docker container를 설정합니다.

각 roles 및 labels 는 Docker Service 설정 시에 상세히 설명합니다.

# SKP_NETWORKS

Swarm 에서 제공하는 Ingress Network를 설정합니다. Swarm network 의 이름은 networks.json 파일을 통해 설정 가능합니다.

networks.json.template 파일을 networks.json 파일로 복사하여 자신의 상황에 맞게 수정하여 사용합니다.

# SKP_IMAGES

SKP 에서 직접 빌드하여 사용되는 Docker Image 에 대한 설정입니다.

images.json.template 파일을 images.json 파일로 복사하여 자신의 상황에 맞게 수정하여 사용합니다.

# SKP_VOLUMES

SKP 에서는 Docker Cluster 노드에서 수행되는 Docker Service 에서 사용하는 데이터 저장소를 공유하기 위해 Docker Volume 을 생성해 사용합니다.

SKP 에서 사용되는 모든 Docker Service 의 볼륨은 $SKP_HOME/etc/volumes.json 파일에 정의 되어 지고 Cluster Docker Serivce 간 공유를 위해 Docker Serivce 가 시작 되기 전에 미리 생성되어야 합니다.

제공되는 template 중에 자신에게 맞는 template 을 복사하여 수정합니다.

* Cluster: volumes_cluster.vagrant.json.template, volumes_cluster.baremetal.json.template
* Single: volumes_singe.vagrant.json.template

지원하는 볼륨 타입은 fs, nfs, sshfs, blobfs, s3fs 입니다.

## volume type - fs

해당 볼륨을 사용하는 Docker Service 와 같은 label 을 지정하여 같은 노드에서만 생성하여 서비스할때 사용합니다.

```
"volume-pgsql-skp" : {
  "type" : "fs",
  "labels" : [
    "pgsql"
  ],
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-pgsql-skp"
  ],
  "path" ; "$SKP_MNT/volume-pgsql-skp"
},
```

## volume type - nfs

해당 볼륨을 Cluster 내의 여러 Docker Service 가 공유해야 할 경우 사용합니다.

```
"volume-registry-skp" : {
  "type" : "nfs",
  "opts" : [
    "--driver local",
    "--opt type=nfs",
    "--opt o=addr=192.168.0.51,rw",
    "--opt device=:$SKP_MNT/volume-registry-skp"
  ],
  "path" : "$SKP_MNT/volume-registry-skp"
}
```

## Volume type - sshfs

SSHFS 외부 저장소를 Cluster Docker Serivce 에서 접근해야 할때 설정하여 사용합니다. 여기서는 예로 내부 Cluster VM 중 c01 에 접속하도록 하겠습니다.

```
"volume-sshfs" : {
  "type" : "sshfs",
  "opts" : [
    "-o sshcmd=vagrant@10.0.0.1:/home/vagrant"
  ],
  "conn" : "vagrant@10.0.0.1"
}
```

## Volume type - blobfs

Azure BLOB 외부 저장소를 Cluster Docker Serivce 에서 접근해야 할때 설정하여 사용합니다.

```
"volume-blobfs" : {
  "type" : "blobfs",
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-blobfs"
  ],
  "path" : "$SKP_MNT/volume-blobfs",
  "account_name" : "YOUR ACCOUNT_NAME",
  "account_key" : "YOUR ACCOUNT_KEY",
  "container_name" : "YOUR CONTAINER_NAME"
}
```

## Volume type - s3fs

AWS S3 외부 저장소를 Cluster Docker Serivce 에서 접근해야 할때 설정하여 사용합니다.

```
"volume-s3fs" : {
  "type" : "s3fs",
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-s3fs"
  ],
  "path" : "$SKP_MNT/volume-s3fs",
  "account_id" : "YOUR ACCOUNT_ID",
  "account_key" : "YOUR ACCOUNT_KEY",
  "bucket" : "YOUR BUCKET"
}
```

# SKP_SERVICES

SKP 에서는 Docker Cluster 노드에서 수행되는 Docker Service 들을 정의합니다.

제공되는 template 중에 자신에게 맞는 template 을 복사하여 수정합니다.

* Cluster: services_cluster.json.template
* Single: services_singe.json.template
