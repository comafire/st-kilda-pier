# Spark

Spark Cluster는 Spark 에서 자체적으로 제공하는 Standalone 모드로 동작합니다. Single 노드일 경우에는 설치 없이 Jupyter Service 내에서 Local 모드로 사용 가능합니다.

## Image

Spark Cluster 는 Jupyter 서비스에 사용된 "skp/docker-ds" 또는 GPU 이미지인 "skp/docker-ds-gpu"를 사용합니다.

생성하지 않았다면 Jupyter 서비스 설정 파일의 Image 섹션을 참조해 주세요.

## Label

SKP_HOSTS 에서 Spark 서비스가 수행될 노드에 spark-master/spark-worker label 을 설정합니다.

```
{
  "c01" : {
    "ipv4" : "192.168.0.51",
    "labels" : {
      ...
      "spark-master" : "enable",
      ...
    },
    "roles" : ["master", "manager"]
  },
  "c02" : {
    "ipv4" : "192.168.0.52",
    "labels" : {
      ...
      "spark-worker" : "enable",
      ...
    },
    "roles" : ["slave", "manager"]
  },
  "c03" : {
    "ipv4" : "192.168.0.53",
    "labels" : {
      ...
      "spark-worker" : "enable",
      ...
    },
    "roles" : ["slave", "manager"]
  },
  "c04" : {
    "ipv4" : "192.168.0.54",
    "labels" : {
      ...
      "spark-worker" : "enable",
      ...
    },
    "roles" : ["slave", "worker"]
  },
  "c05" : {
    "ipv4" : "192.168.0.55",
    "labels" : {
      ...
      "spark-worker" : "enable",
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

Spark 서비스는 분석 수행을 위해 Jupyter 서비스의 볼륨 및 데이터 볼륨을 공유합니다.

## Service

SKP_SERVICES 파일에 Spark Master 및 Worker 서비스를 설정합니다.

```
"spark-master-skp" : {
  "label" : "spark-master",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
    "8030:8080"
  ],
  "environments" : [
    "SKP_SHOME=$SKP_SHOME",
    "SKP_SMNT=$SKP_SMNT"
  ],
  "volumes" : [
    "volume-skp:$SKP_SHOME",
    "volume-jupyter-skp:$SKP_SMNT/volume-jupyter-skp",
    "volume-sshfs:$SKP_SMNT/volume-sshfs",
    "volume-blobfs:$SKP_SMNT/volume-blobfs",
    "volume-s3fs:$SKP_SMNT/volume-s3fs",
    "volume-dfs:$SKP_SMNT/volume-dfs"
  ],
  "cmd" : "$SKP_SHOME/volume/bin/run_spark_master.sh",
  "image" : "localhost:5000/skp/docker-ds:latest",
  "docker" : "docker"
},

"spark-worker-skp" : {
  "label" : "spark-worker",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
  ],
  "environments" : [
    "SKP_SHOME=$SKP_SHOME",
    "SKP_SMNT=$SKP_SMNT",
    "SPARK_URL=spark://spark-master-skp:7077"
  ],
  "volumes" : [
    "volume-skp:$SKP_SHOME",
    "volume-jupyter-skp:$SKP_SMNT/volume-jupyter-skp",
    "volume-sshfs:$SKP_SMNT/volume-sshfs",
    "volume-blobfs:$SKP_SMNT/volume-blobfs",
    "volume-s3fs:$SKP_SMNT/volume-s3fs",
    "volume-dfs:$SKP_SMNT/volume-dfs"
  ],
  "cmd" : "$SKP_SHOME/volume/bin/run_spark_worker.sh",
  "image" : "localhost:5000/skp/docker-ds:latest",
  "docker" : "docker"
},
```

Spark Cluster 를 시작합니다.

```
./skp.sh docker.run -n spark-master-skp
./skp.sh docker.run -n spark-worker-skp
```

정상적으로 시작이 되었다면, Master 노드의 Web Service Port (8030) 으로 접속하면 아래와 같은 상태 Web UI 를 보실 수 있습니다.

ex) http://192.168.0.51:8030

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-003.png"></img>

아래 명령을 통해서 Spark Cluster 를 정지할 수 있습니다.

```
./skp.sh docker.rm -n spark-worker-skp
./skp.sh docker.rm -n spark-master-skp
```
