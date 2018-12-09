SKP를 사용하기 위한 Bare Metal 또는 Vagrant 기본 설치를 마친 이후의 설치에 대해 다룹니다.

# Docker

Docker 에서는 Machine/Swarm/Compose 를 통해 편리한 Docker Container 관리를 제공해 줍니다.

SKP 에서는 Docker 기능을 최대한 활용하여 Cluster를 구축합니다. 다른 유명한 Cluster 관리 툴들이 있지만, 설치 및 사용을 위해 필요한 러닝커브가 상당하기에 Docker Swarm 을 사용합니다.

SKP의 Service는 아래와 같은 이유로 자체 JSON 포맷의 설정파일을 통해 Python Invoke를 이용하여 원격으로 Docker에 대한 동적 명령을 수행하는 방식으로 Container를 관리합니다.
* 통합된 환경 설정 값 적용
* Task 수행 전후 프로세스를 지원
* Docker Volume Plugin 이 지원되지 않는 볼륨 타입을 위한 FUSE를 통한 Bind Mount 방식의 외부 볼륨 지원

Docker Image는 Docker Registry 를 통해 공유시 원격 Registry 를 구축하는 것이 일반적이지만, 이 또한 많은 설정에 시간이 걸리고, 사용범위가 Cluster 내부의 Docker Image 공유이기 때문에 Master 노드에서 빌드 후 NFS 공유 스토리지를 이용하여 각 노드에 local registry로 이미지를 공유하는 방법을 사용합니다.

그외 외부 서비스들은 최대한 Docker Machine/Swarm/Compose 를 활용한 Stack 을 만들어 제공합니다.

## Install

모든 노드에 Docker 를 설치합니다. Docker 설치 명령에는 sudo 없이 docker 명령을 수행하기 위한 usermod 포함되어 있습니다. 적용을 위해 SSH에 재접속합니다.

```
./skp.sh docker.install
exit
vagrant ssh c01
```

Docker 설치 중 아래와 같이 GPG KEY 에러가 나며 진행이 되지 않는 경우는 해당 키를 모든 노드에 등록해 주고 다시 재설치 합니다.

```
W: GPG error: https://download.docker.com/linux/ubuntu xenial InRelease: The following signatures couldn't be verified because the public key is not available: NO_PUBKEY 7EA0A9C3F273FCD8

./skp.sh ssh.cmd -c="sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 7EA0A9C3F273FCD8"
```

## Docker-Machine

Remote 머신의 Docker 컨트롤을 쉽게 하기 위해 Docker-Machine 을 설치 및 등록합니다.

등록될 노드는 SKP_HOSTS 파일을 통해 등록된 노드들 입니다.

```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    ...
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    ...
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    ...
  },
  "c04" : {
    "ipv4" : "192.168.0.54",
    ...
  },
  "c05" : {
    "ipv4" : "192.168.0.55",
    ...
  }
}

```

아래 명령을 순차적으로 수행하여 Docker-Machine 을 설치하고 노드들을 등록합니다.

```
./skp.sh docker.machine-install
./skp.sh docker.machine-create
./skp.sh docker.machine-ls

docker-machine ls
NAME   ACTIVE   DRIVER    STATE     URL                       SWARM   DOCKER     ERRORS
c01    -        generic   Running   tcp://192.168.0.51:2376           v18.09.0   
c02    -        generic   Running   tcp://192.168.0.52:2376           v18.09.0   
c03    -        generic   Running   tcp://192.168.0.53:2376           v18.09.0   
c04    -        generic   Running   tcp://192.168.0.54:2376           v18.09.0   
c05    -        generic   Running   tcp://192.168.0.55:2376           v18.09.0   
```

## Docker-Swarm

Swarm 에서 제공하는 Ingress Network를 설정합니다. Swarm network 의 이름은 SKP_NETWORKS 파일을 통해 설정 가능합니다.

Ingress Network 는 Swarm 에서 제공하는 Network 로 간편하게 Port 기반의 로드 밸런싱을 제공해주는 유용한 Virtual Network 입니다.

```
{
  "net-skp" : {
    "opts" : [
      "--attachable --driver overlay"
    ]
  }
}
```

Swarm Manager 와 Worker 노드 설정 및 해당 노드에서 수행할 Docker Service Label 설정은 SKP_HOSTS 파일에 설정합니다.

Swarm Manager 의 경우 노드가 충분하다면 보통 3개의 Manager를 사용합니다.

```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    ...
    "roles" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    ...
    "roles" : ["slave", "manager"]
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    ...
    "roles" : ["slave", "manager"]
  },
  "c04" : {
    "ipv4" : "192.168.0.54",
    ...
    "roles" : ["slave", "worker"]
  },
  "c05" : {
    "ipv4" : "192.168.0.55",
    ...
    "roles" : ["slave", "worker"]
  }
}
```

설정 후 차례대로 아래 명령 수행을 통해 swarm을 구성하고 ingress network를 생성하고 label 을 적용하고 확인합니다.

```
./skp.sh docker.swarm-init
./skp.sh docker.swarm-join
./skp.sh docker.swarm-label
./skp.sh docker.network-create
./skp.sh docker.node-ls

docker node ls
ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS      ENGINE VERSION
6e8ogpkuenispg4d6a4hs8w3g *   c01                 Ready               Active              Leader              18.09.0
xexa6b28bkwsfbmp61b0jis78     c02                 Ready               Active              Reachable           18.09.0
mlrqiimyg64tchu40gozu10nq     c03                 Ready               Active              Reachable           18.09.0
rs5781nxs49k5rs6k94pbicxb     c04                 Ready               Active                                  18.09.0
xqdli6wxqiy6e1gdpa67fig9g     c05                 Ready               Active                                  18.09.0


./skp.sh docker.network-ls

docker network ls
NETWORK ID          NAME                DRIVER              SCOPE
b5afb2fb00f8        bridge              bridge              local
d185dd9ff3e3        docker_gwbridge     bridge              local
b60c8f49a02c        host                host                local
9jry4t0r6caf        ingress             overlay             swarm
zm4ivslakk5k        net-skp             overlay             swarm
ff9ee5bf6801        none                null                local
```

## Docker-Volume

SKP 에서는 Docker Cluster 노드에서 수행되는 Docker Service 에서 사용하는 데이터 저장소를 공유하기 위해 Docker Volume 을 생성해 사용합니다.

SKP 에서 사용되는 모든 Docker Service 의 볼륨은 SKP_VOLUMES 파일에 정의 되어 지고 Cluster Docker Serivce 간 공유를 위해 Docker Serivce 가 시작 되기 전에 미리 생성되어야 합니다.

지원하는 볼륨 타입은 fs, nfs, sshfs, blobfs, s3fs 입니다.

필요한 볼륨을 직접 정의해서 사용할 수 있지만, 각 서비스에 필수적인 볼륨은 아래 설정 파일을 참조해서 생성해야 합니다.

제공되는 template 중에 자신에게 맞는 template 을 복사하여 수정합니다.

* Cluster: volumes_cluster.vagrant.json.template, volumes_cluster.baremetal.json.template
* Single: volumes_singe.vagrant.json.template

### volume type - fs

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

### volume type - nfs

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

이 볼륨을 위해서는 sudo vi /etc/exports 파일에 공유하고자 디렉토리에 대하여 NFS 설정을 해야 합니다.

접근 네트워크는 사용하시는 IP 에 따라 다르게 설정하면 됩니다, 여기서는 노드들이 192.168.0.x 대 IP 를 사용하기에 192.168.0.0/24 으로 설정하였습니다.

```
/home/vagrant/mnt/volume-registry-skp 192.168.0.0/24(rw,insecure,no_root_squash,no_subtree_check,sync)
```

공유를 위한 디렉토리를 생성하고, nfs 서버를 마운트를 적용 및 확인합니다.

```
./skp.sh nfs.restart
./skp.sh nfs.exportfs
```

### Volume type - sshfs

SSHFS 외부 저장소를 Cluster Docker Serivce 에서 접근해야 할때 설정하여 사용합니다. 여기서는 예로 내부 Cluster VM 중 c01 에 접속하도록 하겠습니다.

```
"volume-sshfs" : {
  "type" : "sshfs",
  "opts" : [
    "-o sshcmd=vagrant@192.168.0.51:/home/vagrant"
  ],
  "conn" : "vagrant@192.168.0.51"
},
```

이 타입을 볼륨을 사용하기 위해서 Docker 의 플러그인을 설치하고 해당 서버에 접속할 수 있도록 SSH 키 교환을 수행합니다.

```
./skp.sh docker.sshfs-plugin-install
./skp.sh docker.sshfs-copy-id -n="volume-sshfs" -p="vagrant"
```

### Volume type - blobfs

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

### Volume type - s3fs

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

### Volume Create

사용하고자하는 Volume 설정이 끝나면 아래 명령으로 설정된 볼륨 전체를 한번에 생성을 할 수 있습니다.

```
./skp.sh docker.volume-create
```

하지만, 서비스 생성시 필요한 볼륨을 생성하면서 진행하는 것이 오류가 생겼을시 대응하기 편하기 때문에 여기서는 SKP_HOME 을 위한 Docker Volume 만을 생성합니다.

```
./skp.sh docker.volume-create -n volume-skp
```

아래 명령을 이용하여 생성한 볼륨에 대한 마운트가 잘되는지 테스트해봅니다. 잘되었다면 /root/skp 위치에서 해당 볼륨에 저장된 데이터들이 보여야 합니다.

```
docker run -it --rm --name shell -v volume-skp:/root/skp ubuntu /bin/bash
```

각 서비스 마다 필요한 볼륨은 각 서비스에서 다시 설명합니다.
