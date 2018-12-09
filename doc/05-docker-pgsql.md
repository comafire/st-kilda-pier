# MySQL

SKP에서 사용하기 위한 RDB 중 하나로 PostgreSQL 을 설정하고 실행 할 수 있습니다.

## Image

PretgreSQL은 공유된 Docker Image를 사용합니다.

## Label

SKP_HOSTS 파일에 label을 설정합니다.

```
"c01" : {
  "ipv4" : "192.168.0.51",
  "labels" : {
    ...
    "pgsql" : "enable",
    ...
  },
  "roles" : ["master", "manager"]
```

## Volume

SKP_VOLUMES 파일에 볼륨을 설정합니다.

```
"volume-pgsql-skp" : {
  "type" : "fs",
  "labels" : [
    "pgsql"
  ],
  "opts" : [
    "--driver local",
    "--opt type=none",
    "--opt o=bind",
    "--opt device=$SKP_MNT/volume-pgsql-skp"
  ],
  "path" : "$SKP_MNT/volume-pgsql-skp"
}
```

볼륨을 생성합니다.

```
./skp.sh docker.volume-create -n="volume-pgsql-skp"
```

#### Service

SKP_SERVICES 파일에 서비스를 설정합니다.

```
"pgsql-skp" : {
  "label" : "pgsql",
  "networks" : [
    "net-skp"
  ],
  "ports" : [
    "5432:5432"
  ],
  "environments" : [
    "PGDATA=/var/lib/pgsql/data",
    "PGSQL_ROOT_PASSWORD=pgsql-pw"
  ],
  "volumes" : [
    "volume-pgsql-skp:/var/lib/pgsql"
  ],
  "image" : "postgres:latest"
},
```

서비스 수행

```
./skp.sh docker.run -n pgsql-skp
```

pgsql client 를 통해서 PostgreSQL 컨테이너에 접속하고 싶다면, 아래 명령을 이용하면 됩니다.

```
./skp.sh docker.pgsql-client -h="c01" -n="pgsql-skp"

psql (11.1 (Debian 11.1-1.pgdg90+1))
Type "help" for help.

postgres=#
```

아래 명령을 통해서 PostgreSQL 를 정지할 수 있습니다.

```
./skp.sh docker.rm -n pgsql-skp
```
