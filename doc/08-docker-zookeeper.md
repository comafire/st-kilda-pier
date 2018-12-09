# Zookeeper

## Image

SKP_IMAGES 파일에 skp/docker-zookeeper 이미지를 설정합니다.

```
{
  ...
  "skp/docker-zookeeper" : {
    "opts" : [
    ],
    "registry" : "localhost:5000",
    "path" : "skp/docker-zookeeper",
    "image" : "skp/docker-zookeeper",
    "tag" : "latest"
  }
  ...
}
```

이미지를 빌드 합니다.

```
./skp.sh docker.image-build -n="skp/docker-zookeeper"
```

## Label

SKP_HOSTS 파일에서 Zookeeper 서비스가 수행될 노드에 zookeeper label 을 설정합니다.

(보통 Zookeeper 는 3개 노드를 기본으로 사용하며, 리더 선정 알고리즘으로 인해 홀 수의 노드로 셋팅 되어야 합니다.)


```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    "labels" : {
      ...
      "zookeeper" : "enable",
      ...
    },
    "roles" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    "labels" : {
      ...
      "zookeeper" : "enable",
      ...
    },
    "roles" : ["slave", "manager"]
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    "labels" : {
      ...
      "zookeeper" : "enable",
      ...
    },
    "roles" : ["slave", "manager"]
  },
  ...
}
```

설정된 label 을 전체 Cluster 에 적용합니다.

```
./skp.sh docker.swarm-label
```

## Service

SKP_SERVICES 파일에 Zookeeper 서비스 설정을 합니다.

```
"zookeeper-skp" : {
  "label" : "zookeeper",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
    "2181:2181", "2888:2888", "3888:3888"
  ],
  "volumes" : [
    "$SKP_MNT/volume-zookeeper-skp/conf/zoo.cfg:/opt/zookeeper/conf/zoo.cfg",
    "$SKP_MNT/volume-zookeeper-skp/data:/opt/zookeeper/data"
  ],
  "path" : "$SKP_MNT/volume-zookeeper-skp",
  "image" : "skp/docker-zookeeper"
}
```

Zookeeper 서비스는 Volume 을 공유하지 않고 path 옵션을 통해 직접 노드 상에 데이터 디렉토리를 생성해서 사용합니다.

서비스를 수행합니다.

```
./skp.sh docker.run -n="zookeeper-skp"
```
