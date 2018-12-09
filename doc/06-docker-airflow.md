# Airflow

SKP에서 Data Science Workflow 를 컨트롤하기 위해 Airflow를 설정하고 실행 할 수 있습니다.

## Image

Airflow 는 Jupyter 서비스에 사용된 "skp/docker-ds" 또는 GPU 이미지인 "skp/docker-ds-gpu"를 사용합니다.

생성하지 않았다면 Jupyter 서비스 설정 파일의 Image 섹션을 참조해 주세요.

## Label

SKP_HOSTS 파일에 label을 설정합니다.

```
"c01" : {
  "ipv4" : "192.168.0.51",
  "labels" : {
    ...
    "airflow" : "enable",
    ...
  },
  "roles" : ["master", "manager"]
```

## Volume

SKP_VOLUMES 파일에 볼륨을 설정합니다.

```
"volume-airflow-skp" : {
  "type" : "fs",
  "labels" : [
    "airflow"
  ],
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-airflow-skp"
  ],
  "path" : "$SKP_MNT/volume-airflow-skp"
}
```

볼륨을 생성합니다.

```
./skp.sh docker.volume-create -n="volume-airflow-skp"
```

#### Service

SKP_SERVICES 파일에 서비스를 설정합니다.

```
"airflow-skp" : {
  "label" : "airflow",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
    "8040:8080"
  ],
  "environments" : [
    "SKP_SHOME=$SKP_SHOME",
    "SKP_SMNT=$SKP_SMNT",
    "AIRFLOW_HOME=$SKP_SHOME/volume/var/airflow",
    "AIRFLOW_DB=airflow",
    "AIRFLOW_DB_USER=airflow",
    "AIRFLOW_DB_PASSWORD=airflow-pw",
    "AIRFLOW__CORE__SQL_ALCHEMY_CONN=mysql://airflow:airflow-pw@mysql-skp/airflow"
  ],
  "volumes" : [
    "volume-skp:$SKP_SHOME",
    "volume-jupyter-skp:$SKP_SMNT/volume-jupyter-skp",
    "volume-sshfs:$SKP_SMNT/volume-sshfs",
    "volume-blobfs:$SKP_SMNT/volume-blobfs",
    "volume-s3fs:$SKP_SMNT/volume-s3fs",
    "volume-dfs:$SKP_SMNT/volume-dfs"
  ],
  "cmd" : "$SKP_SHOME/volume/bin/run_airflow.sh",
  "image" : "localhost:5000/skp/docker-ds:latest",
  "docker" : "docker"
}
```

Airflow를 위한 DB 초기화를 진행합니다.

MySQL를 사용하는 경우

```
./skp.sh docker.mysql-create-airflow-db -h c01 -n mysql-skp:airflow-skp
./skp.sh docker.airflow-init-db -h c01 -n airflow-skp
```

서비스 수행

```
./skp.sh docker.run -n="airflow-skp"
```

정상적으로 시작이 되었다면, Master 노드의 Port (8040) 으로 접속하면 아래와 같은 상태 Web UI 를 보실 수 있습니다.

ex) http://192.168.0.51:8040

<img width="768" src="https://raw.githubusercontent.com/comafire/st-kilda-pier/master/doc/images/2018-st-kilda-pier-004.png"></img>

아래 명령을 통해서 Airflow 를 정지할 수 있습니다.

```
./skp.sh docker.rm -n="airflow-skp"
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
./skp.sh docker.airflow-init-web-passwd -h c01 -n airflow-skp
```

이제 설정한 암호를 통해 Airflow Web UI 에 접속할 수 있습니다.
