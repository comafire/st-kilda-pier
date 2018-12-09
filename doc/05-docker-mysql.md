# MySQL

SKP에서 사용하기 위한 RDB 중 하나로 MySQL 을 설정하고 실행 할 수 있습니다.

## Image

MySQL는 공유된 Docker Image를 사용합니다.

## Label

SKP_HOSTS 파일에 mysql label을 설정합니다.

```
"c01" : {
  "ipv4" : "192.168.0.51",
  "labels" : {
    ...
    "mysql" : "enable",
    ...
  },
  "roles" : ["master", "manager"]
```

## Volume

SKP_VOLUMES 파일에 볼륨을 설정합니다.

```
"volume-mysql-skp" : {
  "type" : "fs",
  "labels" : [
    "mysql"
  ],
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-mysql-skp"
  ],
  "path" : "$SKP_MNT/volume-mysql-skp"    
}
```

볼륨을 생성합니다.

```
./skp.sh docker.volume-create -n="volume-mysql-skp"
```

#### Service

SKP_SERVICES에 서비스를 설정합니다.

```
"mysql-skp" : {
  "label" : "mysql",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
    "3306:3306"
  ],
  "environments" : [
    "MYSQL_ROOT_HOST=%",
    "MYSQL_ROOT_PASSWORD=mysql-pw"
  ],
  "volumes" : [
    "volume-mysql-skp:/var/lib/mysql"
  ],
  "image" : "mysql/mysql-server:latest"
},
```

서비스 수행

```
./skp.sh docker.run -n mysql-skp
```

mysql client 를 통해서 MySQL 컨테이너에 접속하고 싶다면, 아래 명령을 이용하면 됩니다.

```
./skp.sh docker.mysql-client -h="c01" -n="mysql-skp"

mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 310
Server version: 8.0.13 MySQL Community Server - GPL

Copyright (c) 2000, 2018, Oracle and/or its affiliates. All rights reserved.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql>
```

아래 명령을 통해서 MySQL 를 정지할 수 있습니다.

```
./skp.sh docker.rm -n mysql-skp
```
