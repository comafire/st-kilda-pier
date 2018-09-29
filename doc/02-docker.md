# Docker

Docker 에서는 Machine/Swarm/Compose 를 통해 편리한 서버 관리를 제공해 줍니다.

SKP 에서는 Docker 기능을 최대한 활용하여 Cluster를 구축합니다. 다른 유명한 Cluster 관리 툴들이 있지만, 설치 및 사용을 위해 필요한 러닝커브가 아직까지는 상당하기에 Docker Swarm 을 선택하였습니다.

SKP 는 Docker Volume 사용시 FUSE를 통한 privileged 권한을 사용합니다. 하지만, 현재까지는 Swarm/Compose 에서는 제공하고 있지 않아 Docker 명령만을 사용하여 Container를 관리합니다.

Docker Image는 Docker Registry 를 통해 공유시 원격 Registry 를 구축하는 것이 일반적이지만, 이 또한 많은 설정에 시간이 걸리고, 사용범위가 Cluster 내부의 Docker Image 공유이기 때문에 Master 노드에서 빌드 후 NFS 공유 스토리지를 이용하여 각 노드에 local registry로 이미지를 공유하는 방법을 사용합니다.

## Setup Swarm

Swarm 에서 제공하는 Ingress Network를 설정합니다. Swarm network 의 이름은 $SKP_HOME/bin/env.sh 파일을 통해 설정 가능합니다.

Ingress Network 는 Swarm 에서 제공하는 Network 로 간편하게 Port 기반의 로드 밸런싱을 제공해주는 유용한 Virtual Network 입니다.

```
export SKP_NET="net-skp"
```

Swarm Manager 와 Worker 노드 설정은 $SKP_HOME/etc/hosts.json 파일에서 groups를 통해 설정해야 합니다.

```
{
  "c01" : {
    "ipv4" : "10.0.0.4",
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
    "ipv4" : "10.0.0.5",
    "labels" : [
        {"spark-worker" : "enable"}
    ],
    "groups" : ["manager"]
  },
  ...
  "c05" : {
    "ipv4" : "10.0.0.6",
    "labels" : [
        {"spark-worker":"enable"}
    ],
    "groups" : ["worker"]
  }
}
```

설정 후 차례대로 아래 명령 수행을 통해 swarm을 구성하고 ingress network를 구성합니다.

```
./skp.sh docker.swarm-init
./skp.sh docker.swarm-join
./skp.sh docker.swarm-label
./skp.sh docker.swarm-network
```

올바르게 구성되었다면 Master 노드에서 docker node ls 명령으로 swarm node 를 보실수 있습니다.

```
docker node ls

ID                            HOSTNAME            STATUS              AVAILABILITY        MANAGER STATUS      ENGINE VERSION
mpwzlvhl1l9inkxk0d89fw7f2 *   c01                 Ready               Active              Leader              18.06.1-ce
...
6lvs6jav9ikm31fvv22aytjcq     c05                 Ready               Active                                  18.06.1-ce
```

docker network ls 명령으로 swarm ingress network 도 확인하실 수 있습니다.

```
NETWORK ID          NAME                DRIVER              SCOPE
b8d1e13cad65        bridge              bridge              local
...
k2k3p1j7l253        net-skp           overlay             swarm
```

## Run Registry

Cluster 에서 Docker Image 를 공유하기 위한 local registry 를 실행합니다.

local registry는 모든 노드에서 수행되며 Master의 build image를 공유하게 됩니다.

```
./skp.sh docker.registry-run
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

아래 명령을 통해서 Registry 를 정지할 수 있습니다.

```
./skp.sh docker.registry-rm
```

주의사항

```
filesystem layer verification failed for digest sha256:c3d73fc284d6c3350a83cd5125af8af011a5aa426368b6619fab1a85234cad92
```

local registry 에서 image 를 pull 할때 위와 같은 sha digest 에러가 날 경우 시스템 DNS 설정이 제대로 되지 않아 타임 동기화 문제로 발생할 가능성이 높습니다.

DNS 설정과 시스템 시간을 확인해 주세요.

## Build Image

SKP 를 위해 필요한 Docker Image를 Docker File을 통해 Docker Image 를 빌드 한 후 Registry 에 Push 하여 다른 노드와 공유 합니다.

빌드가 필요한 이미지는 아래와 같습니다.
* skp/docker-ds: Data Science for CPU
* skp/docker-ds-gpu: Data Science for GPU
* skp/docker-zookeeper: Zookeeper
* skp/docker-kafka: Kafka

```
./skp.sh docker.image-build-ds -l="ko_KR.UTF-8" -g="FALSE" -t="latest"
./skp.sh docker.image-build-ds -l="ko_KR.UTF-8" -g="TRUE" -t="latest"
./skp.sh docker.image-build-zookeeper -t="latest"
./skp.sh docker.image-build-kafka -t="latest"
```

## Setup Data Volume

Data를 읽고/쓰기 위한 외부 Volume 과의 연동을 위해 SKP 에서는 FUSE를 사용하여 SSH, AWS S3, Azure Blob 과의 연동을 지원합니다.

해당 Data Volume 은 Docker Container 내부에서 Container 기동시 마운트됩니다.

외부 네트워크를 사용하기에 네트워크 전송 속도가 낮으므로, 로컬 네트워크와 같이 네트워크 속도가 충분하지 않다면 Spark Cluster의 작업디렉토리로의 직접적인 사용은 추천하지 않습니다.

## SSHFS

SSH를 통해서 마운트할 서버 정보는 $SKP_HOME/bin/env.sh 파일에서 변경 가능합니다. 사용하지 않을 시에는 모두 "" (빈 스트링) 으로 설정합니다.

```
export SSHFS_ID="sshfs"
export SSHFS_HOST="sshfs.iptime.org"
export SSHFS_VOLUME="/home/sshfs"
```

Docker Container 내에서 SSH 접속을 위한 Key를 생성합니다. 기본적으로 $SKP_HOME/volume/etc/ssh에 생성됩니다.

```
./skp.sh sshfs.keygen
```

생성된 키를 해당 서버에 복사합니다.

```
./skp.sh sshfs.copy-id -p="YOUR PASSWORD"
```

## S3FS

$SKP_HOME/bin/env.sh 파일을 통해 Docker Container 내에서 AWS S3를 마운트 하기 위한 접속 정보를 생성합니다. 사용하지 않을 시에는 모두 "" (빈 스트링) 으로 설정합니다.

```
export S3_ACCOUNT="YOUR_ACCOUNT"
export S3_ACCESS_ID="YOUR_ACCESS_ID"
export S3_ACCESS_KEY="YOUR_ACCESS_KEY"
```

```
./skp.sh s3fs.init
```

## BLOBFS

$SKP_HOME/bin/env.sh 파일을 통해 Docker Container 내에서 Azure Blob을 마운트 하기 위한 접속 정보를 생성합니다. 사용하지 않을 시에는 모두 "" (빈 스트링) 으로 설정합니다.

```
export BLOB_ACCOUNT_NAME="YOUR_ACCOUNT_NAME"
export BLOB_ACCOUNT_KEY="YOUR_ACCOUNT_KEY"
export BLOB_CONTAINER_NAME="YOUR_CONTAINER_NAME"
```

```
./skp.sh blobfs.init
```

# Run Jupyter

Jupyter 관련 설정은 $SKP_HOME/bin/env.sh 에서 변경 가능합니다.

```
# Jupyter
export JUPYTER_NAME="jupyter-skp" # Container Name
export JUPYTER_PORT="8010" # Jupyter Port
export JUPYTER_VOLUME=$SKP_HOME/volume # Jupyter Volume Path
export JUPYTER_PASSWORD="jupyter-pw" # Jupyter Password

export JUPYTER_BASEURL="jupyter-skp" # Jupyter BaseURL, ex) http://localhost:8010/jupyter-skp
export JUPYTER_RESTAPIPORT="8020" # Jupyter Kernel Gateway Port
export JUPYTER_DOCKER="docker" # Docker Command
export JUPYTER_IMAGE="skp/docker-ds" # Docker Image Name
export JUPYTER_TAG="latest" # Docker Image Tag
export JUPYTER_GPU_IMAGE="skp/docker-ds-gpu"
export JUPYTER_GPU_TAG="latest"
export JUPYTER_GPU="FALSE" # if you have a GPU, set TRUE
```

다음 명령을 통해 Data Science Library 가 설치된 Jupyter Container를 실행할 수 있습니다.

```
./skp.sh docker.jupyter-run
```

정상적으로 시작이 되었다면, Master 노드의 Jupyter Port (8010) 으로 접속하여 설정한 패스워드를 입력하면 아래와 같은 상태 Web UI 를 보실 수 있습니다.

ex) http://[Your Public DNS or IP]:8010/jupyter-skp

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-002.png"></img>

아래 명령을 통해서 Jupyter 를 정지할 수 있습니다.

```
./skp.sh docker.jupyter-rm
```

# Run Spark

Spark Cluster는 Spark 에서 자체적으로 제공하는 Standalone 모드로 동작합니다.

$SKP_HOME/bin/env.sh 에서는 Spark Cluster 관련 정보를 설정합니다.

```
# Spark
export SPARK_MNAME="spark-skp-master"
export SPARK_WNAME="spark-skp-worker"
export SPARK_MPORT="8030" # Spark Web Service Port
export SPARK_VOLUME=$SKP_HOME/volume
export SPARK_URL="spark://$SPARK_MNAME:7077"
export SPARK_IMAGE="skp/docker-ds"
export SPARK_TAG="latest"
export SPARK_GPU_IMAGE="skp/docker-ds-gpu"
export SPARK_GPU_TAG="latest"
export SPARK_GPU="FALSE"
```

$SKP_HOME/etc/hosts.json 을 통해 Spark Master 와 Worker 가 수행될 노드를 설정합니다.

```
{
  "c01" : {
    "ipv4" : "10.0.0.4",
    "labels" : [
        ...
        {"spark-master" : "enable"},
        ...
    ],
    "groups" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "10.0.0.5",
    "labels" : [
        ...
        {"spark-worker" : "enable"}
    ],
    "groups" : ["manager"]
  },
  ...
  "c05" : {
    "ipv4" : "10.0.0.8",
    "labels" : [
        ...
        {"spark-worker":"enable"}
    ],
    "groups" : ["worker"]
  }
}
```

아래 명령을 통해서 Spark Cluster 를 시작 할 수 있습니다.

```
./skp.sh docker.spark-run
```

정상적으로 시작이 되었다면, Master 노드의 Web Service Port (8030) 으로 접속하면 아래와 같은 상태 Web UI 를 보실 수 있습니다.

ex) http://[Your Public DNS or IP]:8030

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-003.png"></img>

아래 명령을 통해서 Spark Cluster 를 정지할 수 있습니다.

```
./skp.sh docker.spark-rm
```

# Run Airflow

## Run MySQL

Airflow 를 위한 저장소로 MySQL 을 사용합니다. 아래 명령으로 MySQL 을 실행 할 수 있습니다.

```
./skp.sh docker.mysql-run
```

mysql client 를 통해서 MySQL 컨테이너에 접속하고 싶다면, 아래 명령을 이용하면 됩니다. 암호는 env.sh 파일에 설정된 암호입니다.

```
./skp.sh docker.mysql-client -h="YOUR_HOST_NAME"
```

아래 명령을 통해서 MySQL 를 정지할 수 있습니다.

```
./skp.sh docker.mysql-rm
```

## Init MySQL

Airflow를 위한 DB 초기화를 진행합니다.

```
./skp.sh docker.mysql-airflow-init
./skp.sh docker.airflow-db-init
```

## Run Airflow

Airflow 를 $SKP_HOME/bin/env.sh를 통해 설정하고 수행합니다.

```
# Airflow
export AIRFLOW_NAME="airflow-skp"
export AIRFLOW_PORT="8040"
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
./skp.sh docker.airflow-run
```

정상적으로 시작이 되었다면, Master 노드의 Port (8040) 으로 접속하면 아래와 같은 상태 Web UI 를 보실 수 있습니다.

ex) http://[Your Public DNS or IP]:8040

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-004.png"></img>

아래 명령을 통해서 Airflow 를 정지할 수 있습니다.

```
./skp.sh docker.airflow-rm
```

## Setup Airflow Web Admin Password

Airflow Web UI 의 admin password 를 설정합니다. $SKP_HOME/volume/var/airflow/airflow_init_web_passwd.py 파일에서 암호를 수정합니다.

```
user.username = 'admin'
user.email = 'YOUR_EMAIL'
user.password = unicode("YOUR_PASSWORD", "utf-8")
```

아래 명령을 통하여 Airflow 컨테이너 안에서 초기화 코드를 실행합니다.

```
./skp.sh docker.airflow-web-passwd-init
```

이제 설정한 암호를 통해 Airflow Web UI 에 접속할 수 있습니다.

## Run Portainer

Web GUI를 통해 Docker의 상태를 편하게 볼수 있도록 Portainer를 $SKP_HOME/bin/env.sh 에서 설정하고 실행합니다.

```
export PORTAINER_NAME="portainer-skp"
export PORTAINER_PORT="8050"
```

```
./skp.sh docker.portainer-run
```

이제 Portainer Web UI 를 통해서 초기 Admin 암호를 설정하고 사용할 수 있습니다.

Admin 암호를 설정하면, 아래와 같은 화면을 볼 수 있습니다.

ex) http://[Your Public DNS or IP]:8050

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-005.png"></img>

아래 명령을 통해서 Portainer 를 정지할 수 있습니다.

```
./skp.sh docker.portainer-rm
```


## Run Zookeeper

Kafka Cluster을 위한 Zookeeper를 $SKP_HOME/bin/env.sh 에서 설정하고 실행합니다.

Kafka 에서는 대량의 데이터를 Zookeeper를 통해서 I/O가 일어나기 때문에 ZOOKEEPER_VOLUME 위치는 각 노드의 로컬 스토리지 위치를 권장합니다.

(SKP_HOME 은 NFS를 통해 공유 되므로 대량의 I/O 에는 적합하지 않습니다.)

```
export ZOOKEEPER_NAME="zookeeper-skp"
export ZOOKEEPER_IMAGE="skp/docker-zookeeper"
export ZOOKEEPER_VOLUME="/var/zookeeper"
export ZOOKEEPER_TAG="latest"
```

$SKP_HOME/etc/hosts.json 에서 적용할 노드에 label 을 설정해 줍니다.

(보통 Zookeeper 는 3개 노드를 기본으로 사용하며, 리더 선정 알고리즘으로 인해 홀 수의 노드로 셋팅 되어야 합니다.)

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

다음 명령을 통해 zookeeper 를 수행합니다.

```
./skp.sh docker.zookeeper-run
```

Docker Swarm 의 Ingress Network 에서는 클러스터 컨테이너간 자동 로드 밸런싱 특성으로 인해 컨테이너 이름이 같으면 구분해서 통신이 불가합니다.

zookeeper 의 경우 각 도커 컨테이너간의 구분된 1:1 통신이 가능해야 하기 떄문에 각 노드의 컨테이너 이름 뒤에는 zookeeper id 가 붙게 됩니다.

예를 들어 3대의 노드라면 zookeeper-skp-1, zookeeper-skp-2, zookeeper-skp-3 이런 식입니다.

SKP_NET 의 네트워크와 연결되 다른 컨테이너에서 zookeeper 를 사용해야 한다면 아래와 같이 connection string 을 사용해야 합니다.

zookeeper-skp-1:2181,zookeeper-skp-2:2181,zookeeper-skp-3:2181

## Run Kafka

Kafka Cluster을 $SKP_HOME/bin/env.sh 에서 설정하고 실행합니다.

Kafka 의 경우도 Zookeeper 와 같은 이유로 각 노드의 로컬 스토리지에 마운트 되도록 Volume 경로를 설정을 해 줍니다.

```
export KAFKA_NAME="kafka-skp"
export KAFKA_VOLUME=/var/kafka
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
./skp.sh docker.kafka-run
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
bash-4.4# ./kafka-console-producer.sh --broker-list [Your IP or DNS]:9092 --topic test
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

# Experiment

주의: -v (--volume) 옵션 사용시 path 안에 환경 변수가 들어갈 경우 '' (작은 따움표)를 사용하지 않으면 인식 되지 않습니다. (Python Invoke 버그)

SKP Cluster 내에서 공통 JSON Web Token 이 필요하다면 아래와 같이 flask-skp, nginx-skp, mysql-skp Container 를 이용해 인증 모듈을 구성하여 관리하며, Cluster 내에서 공용 인증 모듈로 사용 가능합니다.

## Run Flask

SKP 에서는 Backend Restful API 를 위한 공통 인증으로 JSON Web Token 을 지원합니다.
개별 Restful API를 서비스하는 프로젝트에서 공통 인증 방식으로 사용할 시에 사용가능합니다.

```
./skp.sh docker.flask-run -n="flask-skp" -p="8060" -v='$SKP_HOME/volume'
```

Flask 에서는 Container 에 접속하여 mysql-skp MySQL Container 에 필요한 DB 를 생성 합니다.

```
./skp.sh docker.flask-shell -h="c01" -n="flask-skp"
root@402b09e07f74:~/volume# cd src/backend/
root@402b09e07f74:~/volume/src/backend# python3 db_create.py
root@402b09e07f74:~/volume/src/backend# python3 db_create_tables.py
root@402b09e07f74:~/volume/src/backend# python3 db_add_account.py
root@402b09e07f74:~/volume/src/backend# exit
```

## Run Nginx

SKP 에서 사용될 Web Admin 페이지를 위한 실행으로 개발 중입니다.

flask-skp 기동 및 DB 생성을 하였다면, 아래 port 로 nginx-skp 에 접속하여 로그인이 가능하며, 로그인 시 사용 가능한 Access Token 이 출력되는 것을 보실 수 있습니다.

```
./skp.sh docker.nginx-run -n='nginx-skp' -p='8070' -v='$SKP_HOME/volume'
```

ex) http://[Your Public DNS or IP]:8070

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-006.png"></img>
