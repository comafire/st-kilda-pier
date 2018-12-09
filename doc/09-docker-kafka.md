# Kafka

## Image

SKP_IMAGES 파일에서 skp/docker-ds 또는 GPU 머신일 경우 skp/docker-ds-gpu 이미지를 설정합니다.

```
{
  "skp/docker-kafka" : {
    "opts" : [
    ],
    "registry" : "localhost:5000",
    "path" : "skp/docker-kafka",
    "image" : "skp/docker-kafka",
    "tag" : "latest"
  }
}
```

이미지를 빌드 합니다.

```
./skp.sh docker.image-build -n="skp/docker-kafka"
```

## Label

SKP_HOSTS 파일에서 Kafka 서비스가 수행될 노드에 kafka label 을 설정합니다.

```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    "labels" : {
      ...
      "kafka" : "enable",
      ...
    },
    "roles" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    "labels" : {
      ...
      "kafka" : "enable"
      ...
    },
    "roles" : ["slave", "manager"]
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    "labels" : {
      ...
      "kafka" : "enable"
      ...
    },
    "roles" : ["slave", "manager"]
  },
  "c04" : {
    "ipv4" : "192.168.0.54",
    "labels" : {
      ...
      "kafka" : "enable"
      ...
    },
    "roles" : ["slave", "worker"]
  },
  "c05" : {
    "ipv4" : "192.168.0.55",
    "labels" : {
      ...
      "kafka" : "enable"
      ...
    },
    "roles" : ["slave", "worker"]
  }
}
```

설정된 label 을 전체 Cluster 에 적용합니다.

```
./skp.sh docker.swarm-label
```

## Volume

SKP_VOLUMES 파일에서 Kafka 서비스에서 사용될 볼륨을 설정합니다.

```
"volume-kafka-skp" : {
  "type" : "fs",
  "labels" : [
    "kafka"
  ],
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-kafka-skp"
  ],
  "path" : "$SKP_MNT/volume-kafka-skp"
}
```

볼륨을 생성합니다.

```
./skp.sh docker.volume-create -n="volume-kafka-skp"
```

## Service

SKP_SERVICES 파일에 Kafka 서비스 설정을 합니다.

```
"kafka-skp" : {
  "label" : "kafka",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
    "9092:9092", "9094:9094"
  ],
  "volumes" : [
    "volume-kafka-skp:/kafka",
    "/var/run/docker.sock:/var/run/docker.sock"
  ],
  "zookeeper" : "zookeeper-skp",
  "image" : "localhost:5000/skp/docker-kafka"
}
```

서비스를 수행합니다.

```
./skp.sh docker.run -n="kafka-skp"
```

테스트

Kafka 컨테이너 내부에 있는 스크립트를 통해 Topic 을 생성하고 메시지 송/수신을 해보겠습니다.

Kafka 컨테이너가 수행되고 있는 노드중 하나 접속해서 Bash Shell 을 수행 합니다.

```
./skp.sh docker.exec-shell -h c01 -n kafka-skp
bash-4.4#
```

이제 test 로 사용할 Kafka Topic 을 생성하고 확인합니다. 클러스터에 떠 있는 총 Kafka 컨테이너 수 만큼 --replication-factor 의 수를 설정 가능합니다.

--replication-factor 의 수는 그 수 만큼 메시지를 복사 해 놓기 때문에 해당 Kafka 중 하나가 중지 되더라도 다른 Kafka 컨테이너를 통해 안전하게 메시지 송/수신이 가능하게 됩니다.

```
bash-4.4# cd /opt/kafka/bin
bash-4.4# ./kafka-topics.sh --zookeeper zookeeper-skp-1:2181,zookeeper-skp-2:2181,zookeeper-skp-3:2181 --create --replication-factor 3 --partitions 1 --topic test

Created topic "test".

bash-4.4# ./kafka-topics.sh --zookeeper zookeeper-skp-1:2181,zookeeper-skp-2:2181,zookeeper-skp-3:2181 --list

test

bash-4.4# ./kafka-topics.sh --zookeeper zookeeper-skp-1:2181,zookeeper-skp-2:2181,zookeeper-skp-3:2181 --describe --topic test

Topic:test	PartitionCount:3	ReplicationFactor:2	Configs:
	Topic: test	Partition: 0	Leader: 4	Replicas: 4,2,3	Isr: 4,2,3
bash-4.4#
```

클러스터 노드의 마스터는 외부 네트워크와 통신이 되도록 해 놓았을 것입니다. 이제 마스터 주소의 IP 주소 또는 DNS로 메세지를 보냅니다. 메시지 전송 전 Kafka 9092 포트의 방화벽이 해제 되어 있는지 체크는 필수 입니다.

```
bash-4.4# ./kafka-console-producer.sh --broker-list 192.168.0.51:9092 --topic test
>hello world!!
>
```

이제 다른 노드의 Kafka 컨테이너에서 Shell 을 수행하여 해당 메세지가 들어 오는지 확인해겠습니다.

```
./skp.sh docker.exec-shell -h c02 -n kafka-skp
bash-4.4#
```

수신자는 내부 컨테이너 중 하나가 될 것이기에 이제 --bootstrap-server 의 값은 kafka-skp:9092 으로 하였으며, 수신된 메시지를 보실 수 있습니다.

```
bash-4.4# cd /opt/kafka/bin
bash-4.4# ./kafka-console-consumer.sh --bootstrap-server kafka-skp:9092 --topic test --from-beginning
hello world!!
```
