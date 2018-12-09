# Portainer

Portainer 는 Docker Swarm 모니터링을 제공하는 Web UI 툴입니다.

## Label

SKP_HOSTS 파일에 label을 설정합니다.

```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    "labels" : {
      ...
      "portainer" : "enable",
      "portainer-agent" : "enable",
      ...
    },
    "roles" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    "labels" : {
      ...
      "portainer-agent" : "enable",
      ...
    },
    "roles" : ["slave", "manager"]
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    "labels" : {
      ...
      "portainer-agent" : "enable",
      ...
    },
    "roles" : ["slave", "manager"]
  },
  "c04" : {
    "ipv4" : "192.168.0.54",
    "labels" : {
      ...
      "portainer-agent" : "enable",
      ...
    },
    "roles" : ["slave", "worker"]
  },
  "c05" : {
    "ipv4" : "192.168.0.55",
    "labels" : {
      ...
      "portainer-agent" : "enable",             
      ...
    },
    "roles" : ["slave", "worker"]
  }
}
```

## Volume

SKP_VOLUMES 파일에 볼륨을 설정합니다.

```
"volume-portainer-skp" : {
  "type" : "fs",
  "labels" : [
    "portainer"
  ],
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-portainer-skp"
  ],
  "path" : "$SKP_MNT/volume-portainer-skp"
}
```

볼륨을 생성합니다.

```
./skp.sh docker.volume-create -n="volume-portainer-skp"
```

#### Service

services.json 설정합니다.

```
"portainer-skp" : {
  "label" : "portainer",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
    "8050:9000"
  ],
  "volumes" : [
    "volume-portainer-skp:/data"
  ],
  "image" : "portainer/portainer",
  "cmd" : "-H 'tcp://portainer-agent-skp:9001' --tlsskipverify "
},
"portainer-agent-skp" : {
  "label" : "portainer-agent",
  "networks" : [
    "net-skp"
  ],
  "environments" : [
    "AGENT_CLUSTER_ADDR=portainer-agent-skp"
  ],
  "volumes" : [
    "/var/run/docker.sock:/var/run/docker.sock",
    "/var/lib/docker/volumes:/var/lib/docker/volumes"
  ],
  "image" : "portainer/agent"
}
```

서비스 수행

```
./skp.sh docker.run -n="portainer-skp"
./skp.sh docker.run -n="portainer-agent-skp"
```

정상적으로 시작이 되었다면, Master 노드의 Port (8050) 으로 접속하면 아래와 같은 상태 Web UI 를 보실 수 있습니다.

ex) http://192.168.0.51:8050

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-005.png"></img>

아래 명령을 통해서 Portainer 를 정지할 수 있습니다.

```
./skp.sh docker.rm -n="portainer-skp"
```

## Setup Web Admin Password

Portainer는 초기 Web UI 구동시 브라우저를 통해 초기 admin 계정의 password 를 설정합니다.

이 암호를 재성정 하기 위해서는 portainer의 볼륨과 마운트 디렉토리를 삭제하고 다시 생성하는 번거로움을 감수해야 하니 꼭 기억하세요.
