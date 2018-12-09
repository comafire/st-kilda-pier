# Registry

Docker Cluster 에서 Docker Image 를 공유하기 위해 제일 먼저 Registry Service 를 실행합니다.

SKP 에서 필요한 Docker Image는 Master에서 빌드되며 Registry Service 를 통해 모든 노드에서 공유됩니다.

## Label

SKP_HOSTS 에서 모든 노드에 registry label을 설정해 registry 서비스가 모든 노드에서 수행되도록 합니다.

```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    "labels" : {
      "registry" : "enable",
      ...
    },
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    "labels" : {
      "registry" : "enable",
      ...
    },
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    "labels" : {
      "registry" : "enable",
      ...
    },
  },
  "c04" : {
    "ipv4" : "192.168.0.54",
    "labels" : {
      "registry" : "enable",
      ...
    },
  },
  "c05" : {
    "ipv4" : "192.168.0.55",
    "labels" : {
      "registry" : "enable",
      ...
    },
  }
}
```

## Volume

Registry 볼륨은 모든 노드의 Registry 서비스에서 공유해야 하기 때문에 NFS 타입으로 설정합니다.

/etc/exports 파일에 NFS 공유 설정을 합니다.

```
/home/vagrant/mnt/volume-registry-skp 192.168.0.0/24(rw,insecure,no_root_squash,no_subtree_check,sync)
```

NFS 재시작 및 마운트 상태를 확인합니다.

```
./skp.sh nfs.restart
./skp.sh nfs.exportfs
```

SKP_VOLUMES 파일에 Registry 볼륨을 설정합니다.

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
},
```

볼륨 생성합니다.

```
./skp.sh docker.volume-create -n volume-registry-skp
```

## Service

SKP_SERVICES 파일에 Registry 서비스를 설정합니다.

```
"registry-skp" : {
  "label" : "registry",
  "networks" : [
    "net-skp"
  ],
  "ports": [
    "5000:5000"
  ],
  "environments" : [
  ],
  "volumes" : [
    "volume-registry-skp:/var/lib/registry"
  ],
  "image" : "registry:2"
},
```

서비스를 수행합니다.

```
./skp.sh docker.run -n registry-skp
```

모든 노드의 registry container 가 잘 수행되고 있는지 아래 명령으로 확인해 봅니다.

```
./skp.sh docker.ps

docker-machine ssh c01 docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED              STATUS              PORTS                    NAMES
200cba536777        registry:2          "/entrypoint.sh /etc…"   About a minute ago   Up About a minute   0.0.0.0:5000->5000/tcp   registry-skp
...
docker-machine ssh c05 docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
50904e7b2058        registry:2          "/entrypoint.sh /etc…"   27 seconds ago      Up 22 seconds       0.0.0.0:5000->5000/tcp   registry-skp
```

주의사항

```
filesystem layer verification failed for digest sha256:c3d73fc284d6c3350a83cd5125af8af011a5aa426368b6619fab1a85234cad92
```

local registry 에서 image 를 pull 할때 위와 같은 sha digest 에러가 날 경우 시스템 DNS 설정이 제대로 되지 않아 타임 동기화 문제로 발생할 가능성이 높습니다.

DNS 설정과 시스템 시간을 확인해 주세요.
