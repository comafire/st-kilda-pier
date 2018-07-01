# Docker

Docker 에서는 Machine/Swarm/Compose 를 통해 편리한 서버 관리를 제공해 줍니다.

SKP 에서는 Volume 설정에 FUSE를 사용함에 있어, privileged 권한이 필요하지만, 현재 Swarm/Compose 에서는 제공하고 있지 않아 현재는 Docker만을 사용하여 Container를 관리합니다.

Docker Image의 경우 Master 노드에서 빌드 후 각 노드에 local registry를 이용하여 이미지는 공유합니다.

## Setup Swarm

Swarm 에서 제공하는 Ingress Network를 설정합니다. Swarm network 의 이름은 $SKP_HOME/bin/env.sh 파일을 통해 설정 가능합니다.

```
export SWARM_NET="swarm-skp"
```

Swarm Manager 와 Worker 노드 설정은 $SKP_HOME/etc/hosts.json 파일의 groups를 통해 설정 가능합니다.

```
{
  "c01" : {
    "ipv4" : "192.168.50.1",
    "labels" : [
        {"registry" : "enable"},      
        {"jupyter" : "enable"},
        {"spark-master" : "enable"},
        {"portainer" : "enable"},
        {"mysql" : "enable"}
    ],
    "groups" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.50.2",
    "labels" : [
        {"spark-worker" : "enable"}
    ],
    "groups" : ["manager"]
  },
  ...
  "c10" : {
    "ipv4" : "192.168.50.10",
    "labels" : [
        {"spark-worker":"enable"}
    ],
    "groups" : ["worker"]
  }
}
```

설정 후 아래 명령을 통해 swarm을 구성하고 ingress network를 구성합니다.

```
./fab.sh docker_swarm_init
./fab.sh docker_swarm_join
./fab.sh docker_swarm_label
./fab.sh docker_swarm_network
```

올바르게 구성되었다면 Master 노드에서 docker network ls 명령으로 swarm ingress network 를 보실수 있습니다.

```
NETWORK ID          NAME                DRIVER              SCOPE
b8d1e13cad65        bridge              bridge              local
...
k2k3p1j7l253        swarm-skp           overlay             swarm
```

## Run Registry

클러스터에서 Docker Image를 공유하기 위한 local registry를 실행합니다.

local registry는 모든 노드에서 수행되며 Master의 build image를 공유하게 됩니다.

```
./fab.sh docker_run_registry
```

주의사항

```
filesystem layer verification failed for digest sha256:c3d73fc284d6c3350a83cd5125af8af011a5aa426368b6619fab1a85234cad92
```

local registry 에서 image 를 pull 할때 위와 같은 sha digest 에러가 날 경우 시스템 DNS 설정이 제대로 되지 않아 타임 동기화 문제로 발생할 가능성이 높습니다.
DNS 설정과 시스템 시간을 확인해 주세요.

## Build Image

클러스터에서 제공하는 Dockerfile을 통해 Docker Image 를 빌드 후 local registry에 push 합니다.

빌드가 필요한 이미지는 아래와 같습니다.
* skp/docker-ds: Data Science for CPU
* skp/docker-ds-gpu: Data Science for GPU

```
./fab.sh docker_build --set LOCALE="ko_KR.UTF-8",GPU="FALSE",NAME="skp/docker-ds",IMAGE="skp/docker-ds",TAG="latest"
./fab.sh docker_build --set LOCALE="ko_KR.UTF-8",GPU="TRUE",NAME="skp/docker-ds",IMAGE="skp/docker-ds-gpu",TAG="latest"
```

## Setup Data Volume

Data를 읽고/쓰기 위한 외부 Volume 과의 연동을 위해 SKP 에서는 FUSE를 사용하여 SSH, AWS S3, Azure Blob 과의 연동을 지원합니다.

## SSHFS

SSH를 통해서 마운트할 서버 정보는 $SKP_HOME/bin/env.sh 파일에서 변경 가능합니다.

```
export SSHFS_ID="sshfs"
export SSHFS_HOST="sshfs.iptime.org"
export SSHFS_VOLUME="/home/sshfs"
```

접속을 위한 Key를 생성합니다. 기본적으로 $SKP_HOME/volume/etc/ssh에 생성됩니다.

```
./fab.sh sshfs_keygen
```

생성된 키를 해당 서버에 복사합니다.

```
./fab.sh sshfs_copy_id --set SSHFS_PASSWD="YOUR PASSWORD"
```

## S3FS

$SKP_HOME/bin/env.sh 파일을 통해 AWS S3를 마운트 하기 위한 접속 정보를 생성합니다.

```
export S3_ACCOUNT="YOUR_ACCOUNT"
export S3_ACCESS_ID="YOUR_ACCESS_ID"
export S3_ACCESS_KEY="YOUR_ACCESS_KEY"
```

```
./fab.sh s3fs_init
```

## BLOBFS

$SKP_HOME/bin/env.sh 파일을 통해 Azure Blob을 마운트 하기 위한 접속 정보를 생성합니다.

```
export BLOB_ACCOUNT_NAME="YOUR_ACCOUNT_NAME"
export BLOB_ACCOUNT_KEY="YOUR_ACCOUNT_KEY"
export BLOB_CONTAINER_NAME="YOUR_CONTAINER_NAME"
```

```
./fab.sh blobfs_init
```

# Run Jupyter

Jupyter 관련 설정은 $SKP_HOME/bin/env.sh 에서 변경 가능합니다.

```
# Jupyter
export JUPYTER_NAME="jupyter-skp" # Container Name
export JUPYTER_PORT="8110" # Jupyter Port
export JUPYTER_VOLUME=$SKP_HOME/volume # Jupyter Volume Path
export JUPYTER_PASSWORD="jupyter-pw" # Jupyter Password

export JUPYTER_BASEURL="jupyter-skp" # Jupyter BaseURL, ex) http://localhost:8010/jupyter
export JUPYTER_RESTAPIPORT="8120" # Jupyter Kernel Gateway Port
export JUPYTER_DOCKER="docker" # Docker Command
export JUPYTER_IMAGE="skp/docker-ds" # Docker Image Name
export JUPYTER_TAG="latest" # Docker Image Tag
export JUPYTER_GPU_IMAGE="skp/docker-ds-gpu"
export JUPYTER_GPU_TAG="latest"
export JUPYTER_GPU="TRUE"
```

다음 명령을 통해 Jupyter Container를 실행할 수 있습니다.

```
./fab.sh docker_run_jupyter
```

# Run Spark

Spark Cluster를 $SKP_HOME/bin/env.sh 와 $SKP_HOME/etc/hosts.json 을 통해 설정하고 실행합니다.

```
# Spark
export SPARK_MNAME="spark-skp-master"
export SPARK_WNAME="spark-skp-worker"
export SPARK_MPORT="8130" # Spark Web Service Port
export SPARK_VOLUME=$SKP_HOME/volume
export SPARK_URL="spark://$SPARK_MNAME:7077"
export SPARK_IMAGE="skp/docker-ds"
export SPARK_TAG="latest"
export SPARK_GPU_IMAGE="skp/docker-ds-gpu"
export SPARK_GPU_TAG="latest"
export SPARK_GPU="FALSE"
```

```
{
  "c01" : {
    "ipv4" : "192.168.50.1",
    "labels" : [
        ...
        {"spark-master" : "enable"},
        ...
    ],
    "groups" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.50.2",
    "labels" : [
        ...
        {"spark-worker" : "enable"}
    ],
    "groups" : ["manager"]
  },
  ...
  "c10" : {
    "ipv4" : "192.168.50.10",
    "labels" : [
        ...
        {"spark-worker":"enable"}
    ],
    "groups" : ["worker"]
  }
}
```

```
./fab.sh docker_run_spark
```

# Run Airflow

## Run MySQL

Airflow 를 위한 저장소로 MySQL 을 사용합니다. 아래 명령으로 MySQL 을 실행 할 수 있습니다.

```
./fab.sh docker_run_mysql
```

mysql client 를 통해서 MySQL 컨테이너에 접속하고 싶다면, 아래 명령을 이용하면 됩니다. 암호는 env.sh 파일에 설정된 암호입니다.

```
./fab.sh docker_exec_mysql
```

## Init MySQL

Airflow를 위한 DB 초기화를 진행합니다.

```
./fab.sh docker_init_airflow_mysql
./fab.sh docker_init_airflow_db
```

## Run Airflow

Airflow 를 $SKP_HOME/bin/env.sh를 통해 설정하고 수행합니다.

```
# Airflow
export AIRFLOW_NAME="airflow-skp"
export AIRFLOW_PORT="8140"
export AIRFLOW_VOLUME=$SKP_HOME/volume

export AIRFLOW_DB="airflow"
export AIRFLOW_DB_USER="airflow"
export AIRFLOW_DB_PASSWORD="airflow-pw"
export AIRFLOW__CORE__SQL_ALCHEMY_CONN="mysql+pymysql://airflow:airflow@$MYSQL_NAME/airflow"
export AIRFLOW_IMAGE="skp/docker-ds"
export AIRFLOW_TAG="latest"
export AIRFLOW_GPU_IMAGE="skp/docker-ds-gpu"
export AIRFLOW_GPU_TAG="latest"
export AIRFLOW_GPU="FALSE"
```

```
./fab.sh docker_run_airflow
```

## Setup Airflow Web Admin Password

Airflow Web UI 의 admin password 를 설정합니다. $SKP_HOME/volume/var/airflow/airflow_init_web_passwd.py 파일에서 암호를 수정합니다.

```
user.email = 'YOUR_EMAIL'
user.password = unicode("YOUR_PASSWORD", "utf-8")
```

아래 명령을 통하여 Airflow 컨테이너 안에서 초기화 코드를 실행합니다.

```
./fab.sh docker_init_airflow_web_passwd
```

이제 설정한 암호를 통해 Airflow Web UI 에 접속할 수 있습니다.

## Run Portainer

Docker의 상태는 Web GUI를 통해 편하게 볼수 있도록 Portainer를 $SKP_HOME/bin/env.sh 에서 설정하고 실행합니다.

```
export PORTAINER_NAME="portainer-skp"
export PORTAINER_PORT="8150"
export PORTAINER_ID="admin"
export PORTAINER_PW="admin-pw"
```

```
./fab.sh docker_run_portainer
```

## Run Zookeeper

Kafka Cluster을 위한 Zookeeper를 $SKP_HOME/bin/env.sh 에서 설정하고 실행합니다.

```
export ZOOKEEPER_NAME="zookeeper-skp"
export ZOOKEEPER_PORT="2181"
export ZOOKEEPER_IMAGE="skp/docker-zookeeper"
export ZOOKEEPER_VOLUME=$SKP_HOME/volume/var/zookeeper
export ZOOKEEPER_TAG="latest"
```

$SKP_HOME/etc/hosts.json 에서 적용할 노드에 label 을 설정해 줍니다. (보통 Zookeeper 는 3개 노드를 기본으로 사용합니다.)

```
...
"labels" : [
    {"registry" : "enable"},
    {"spark-worker" : "enable"},
    {"zookeeper" : "enable"},
    {"kafka" : "enable"}
],
...
```

```
./fab.sh docker_run_zookeeper
```

## Run Kafka

Kafka Cluster을 $SKP_HOME/bin/env.sh 에서 설정하고 실행합니다.

```
export KAFKA_NAME="kafka-skp"
export KAFKA_ADVERTISED_PORT="9094"
export KAFKA_PORT="9092"
export KAFKA_VOLUME=$SKP_HOME/volume/var/kafka
export KAFKA_IMAGE="skp/docker-kafka"
export KAFKA_TAG="latest"
```

$SKP_HOME/etc/hosts.json 에서 적용할 노드에 label 을 설정해 줍니다.
```
...
"labels" : [
    {"registry" : "enable"},
    {"spark-worker" : "enable"},
    {"zookeeper" : "enable"},
    {"kafka" : "enable"}
],
...
```

```
./fab.sh docker_run_kafka
```

테스트

test topic 생성 후 채널 확인 후 producer 실행하여 hello world 보내보기

```
cd ~/st-kilda-pier/etc/docker-file/skp/docker-kafka
./start-kafka-shell.sh swarm-skp c01 zookeeper-skp:2181
bash-4.4# cd /opt/kafka
bash-4.4# ./bin/kafka-topics.sh --create --zookeeper zookeeper-skp:2181 --replication-factor 2 --partitions 3 --topic test
Created topic "test".
bash-4.4# ./bin/kafka-topics.sh --list --zookeeper zookeeper-skp:2181
test
bash-4.4# ./bin/kafka-topics.sh --describe --topic test --zookeeper zookeeper-skp:2181
Topic:test	PartitionCount:3	ReplicationFactor:2	Configs:
	Topic: test	Partition: 0	Leader: 1005	Replicas: 1005,1006	Isr: 1005,1006
	Topic: test	Partition: 1	Leader: 1006	Replicas: 1006,1005	Isr: 1006,1005
	Topic: test	Partition: 2	Leader: 1005	Replicas: 1005,1006	Isr: 1005,1006
bash-4.4# bin/kafka-console-producer.sh --broker-list c01.iptime.org:9092 --topic test
>hello world!!
>
```

다른 kafka shell 을 열어 해당 test topic 에서 메시지 읽어오기

```
cd ~/st-kilda-pier/etc/docker-file/skp/docker-kafka
./start-kafka-shell.sh swarm-skp c01 zookeeper-skp:2181
bash-4.4# cd /opt/kafka
bash-4.4# ./bin/kafka-console-consumer.sh --bootstrap-server c01.iptime.org:9092 --topic test --from-beginning
hello world!!
```

# Experiment

## Run Nginx

SKP 에서 사용될 Web Admin 페이지를 위한 실행으로 개발 중입니다.

```
./fab.sh docker_run_nginx --set NAME="nginx-skp",PORT="7160",VOLUME="/root/volume"
```

## Run Flask

SKP 에서는 Backend Restful API 를 위한 공통 인증으로 JSON Web Token 을 지원합니다.
개별 Restful API를 서비스하는 프로젝트에서 공통 인증 방식으로 사용할 시에 사용가능합니다.

```
./fab.sh docker_run_flask --set NAME="flask-skp",PORT="7170",VOLUME="/root/volume"
```
