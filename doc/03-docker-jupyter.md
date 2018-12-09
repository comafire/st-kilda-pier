# Jupyter

## Image

SKP_IMAGES 파일에 설정된 skp/docker-ds 또는 GPU 머신일 경우 skp/docker-ds-gpu 이미지를 설정합니다.

```
{
  "skp/docker-ds" : {
    "opts" : [
      "--build-arg locale=en_US.UTF-8",
      "--build-arg gpu=FALSE"
    ],
    "registry" : "localhost:5000",
    "path" : "skp/docker-ds",
    "image" : "skp/docker-ds",
    "tag" : "latest"
  },
  "skp/docker-ds-gpu" : {
    "opts" : [
      "--build-arg locale=en_US.UTF-8",
      "--build-arg gpu=TRUE"
    ],
    "registry" : "localhost:5000",
    "path" : "skp/docker-ds",    
    "image" : "skp/docker-ds-gpu",
    "tag" : "latest"
  }
}
```

이미지를 빌드 합니다.

```
./skp.sh docker.image-build -n="skp/docker-ds"
./skp.sh docker.image-build -n="skp/docker-ds-gpu"
```

## Label

SKP_HOSTS 에서 Jupyter 서비스가 수행될 노드에 jupyter label 을 설정합니다.

```
"c01" : {
  "ipv4" : "192.168.0.51",
  "labels" : {
    ...
    "jupyter" : "enable",
    ...
  },
  "roles" : ["master", "manager"]
},
...
```

설정된 label 을 전체 Cluster 에 적용합니다.

```
./skp.sh docker.swarm-label
```

## Volume

Jupyter 볼륨은 다른 서비스에서 공유되어야 하기 때문에 NFS 타입을 사용합니다.

/etc/exports 파일에 NFS 공유 설정을 합니다.

```
/home/vagrant/mnt/volume-jupyter-skp 192.168.0.0/24(rw,insecure,no_root_squash,no_subtree_check,sync)
```

NFS 재시작 및 마운트 상태를 확인합니다.

```
./skp.sh nfs.restart
./skp.sh nfs.exportfs
```
SKP_VOLUMES 에서 Jupyter 서비스에서 사용될 볼륨을 설정합니다.

```
"volume-jupyter-skp" : {
  "type" : "nfs",
  "opts" : [
    "--driver local",
    "--opt type=nfs",
    "--opt o=addr=192.168.0.51,rw",
    "--opt device=:$SKP_MNT/volume-jupyter-skp"
  ],
  "path" : "$SKP_MNT/volume-jupyter-skp"
},
```

볼륨을 생성합니다.

```
./skp.sh docker.volume-create -n="volume-jupyter-skp"
```

## Service

SKP_SERVICES 에 Jupyter 서비스 설정을 합니다.

```
  "jupyter-skp" : {
    "label" : "jupyter",
    "networks" : [
      "net-skp"
    ],
    "ports" : [
      "8010:8888",
      "8020:8088"
    ],
    "environments" : [
      "SKP_SHOME=$SKP_SHOME",
      "SKP_SMNT=$SKP_SMNT",
      "JUPYTER_PASSWORD=jupyter-pw",
      "JUPYTER_BASEURL=jupyter-skp"
    ],
    "volumes" : [
      "/var/run/docker.sock:/var/run/docker.sock",
      "volume-skp:$SKP_SHOME",
      "volume-jupyter-skp:$SKP_SMNT/volume-jupyter-skp",
      "volume-sshfs:$SKP_SMNT/volume-sshfs",
      "volume-blobfs:$SKP_SMNT/volume-blobfs",
      "volume-s3fs:$SKP_SMNT/volume-s3fs",
      "volume-dfs:$SKP_SMNT/volume-dfs"
    ],
    "cmd" : "$SKP_SHOME/volume/bin/run_jupyter.sh",
    "image" : "localhost:5000/skp/docker-ds:latest",
    "docker" : "docker"
  },
```

서비스를 수행합니다.

```
./skp.sh docker.run -n="jupyter-skp"
```

정상적으로 시작이 되었다면, Master 노드의 Jupyter Port (8010) 으로 접속하여 설정한 패스워드를 입력하면 아래와 같은 상태 Web UI 를 보실 수 있습니다.

ex) http://192.168.0.51:8010/jupyter-skp

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-002.png"></img>

아래 명령을 통해서 Jupyter 를 정지할 수 있습니다.

```
./skp.sh docker.rm -n="jupyter-skp"
```
