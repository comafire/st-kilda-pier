# Cluster

운영체제: Ubuntu 16.04 LTS (아직 Nvidia-Docker 에서 Ubuntu 18.04 LTS 를 지원하고 있지 않기때문에 해당 버전을 사용합니다.)

클러스터 설정 부분은 어느 정도 수동 설정 부분을 포함하고 있습니다.

## Network

클러스터의 네트워크는 Master 노드에 2개 네트워크 카드가 설치되어 있고, 이를 통해서 Public 망과 Private 망으로 연결되는 것으로 가정합니다.

```
Public Network <--> Master <---> Private Network <--> Workers
```

내부 Worker 노드들의 외부 네트워크 사용할 수 있도록 iptable 을 설정합니다.

여기서는 외부망과 연결된 네트워크 카드의 이름을 'pub_eth' 라고 가정하겠습니다.

```
sudo /sbin/iptables -A FORWARD -o pub_eth -j ACCEPT
sudo /sbin/iptables -t nat -A POSTROUTING -o pub_eth -j MASQUERADE
```

재부팅 시에도 적용이 가능하도록 /etc/rc.local 파일에도 아래 내용을 추가해 줍니다.

```
/sbin/iptables -A FORWARD -o pub_eth -j ACCEPT
/sbin/iptables -t nat -A POSTROUTING -o pub_eth -j MASQUERADE
```

이제 worker 노드에서 ping 명령으로 외부 사이트에 접속 가능한지 테스트 해봅니다.

## Setup User

st-kilda-pier 용 계정 skp를 모든 노드에 생성합니다.

```
sudo adduser skp
```

계정 사용시 sudo 명령을 통해 권한을 업그레이드 하는 경우가 많기 때문에 암호 없이 사용 가능하도록 설정합니다.

sudo vi /etc/sudoers 파일을 열어서 sudo 권한 사용자가 암호를 넣지 않아도 되도록 NOPASSWD 설정을 추가합니다.

```
%sudo   ALL=(ALL:ALL) NOPASSWD:ALL
```

그리고 skp 사용자를 sudo 그룹에 추가합니다.

```
sudo usermod -aG sudo skp
```

## Setup Locale

지금 부터 새로 생성된 skp 사용자로 접속하여 설치를 계속 진행합니다.

설치시 시스템 Locale 설정이 되어 있지 않은 경우, 에러가 발생합니다, 각자 원하는 Locale 로 설정해 아래와 같이 Master 노드를 설정해 줍니다, Worker 노드는 추후 명령을 통해 원격 설치를 진행합니다.

```
sudo apt-get install -y language-pack-en && sudo locale-gen en_US.UTF-8 && sudo dpkg-reconfigure locales
```

시스템 설정을 업데이트 합니다.

```
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LC_MESSAGES=POSIX
```

## Install Dependencies

SKP에서는 시스템 Python 과 Python Invoke, SSH 원격 명령 및 Docker-Machine을 이용해서 설치 및 관리를 진행합니다.

이를 위해 Master 노드에 아래 패키지를 설치합니다.

```
sudo apt-get install -y python-pip sshpass && pip install invoke
```

## Install SKP

이제 SKP 를 사용하기 위하여 Master 노드에 소스를 설치합니다.

```
git clone https://github.com/comafire/st-kilda-pier.git
```

### env.sh

설치된 bin 디렉토리내에 env.sh, skp.sh 쉘 스크립트를 통해 주요 환경설정 및 원격 명령을 수행합니다.

[env.sh.templeate](https://github.com/comafire/st-kilda-pier/blob/master/bin/env.sh.templeate) 파일을 env.sh 파일로 복사하여 내부 설정 변수들을 수정합니다.

### hosts.json

설치된 etc 디렉토리내에 hosts.json 파일을 통해 클러스터 노드의 형상을 설정합니다.

[hosts.json.templeate](https://github.com/comafire/st-kilda-pier/blob/master/etc/hosts.json.templeate) 파일을 hosts.json 파일로 복사하여 내부 설졍 변수들을 수정합니다.

hostname 을 키로 사용하여 ipv4, labels, groups 를 설정합니다.

groups 는 docker swarm 에서 수행할 역할을 설정합니다.

* master: spark cluster 의 master
* manager: swarm cluster 의 manager
* worker: spark/swarm cluster 의 worker

labels 는 노드상에서 수행할 docker container를 설정합니다.

설정이 완료된 후에는 skp.sh -l 명령을 통해 사용가능한 명령어 셋이 출력되는지 테스트 해봅니다, 모든 명령은 SKP_HOME 디렉토리안에 bin 폴더 안에서 수행되어야 합니다.

```
cd st-kilda-pier/bin
./skp.sh -l

Available tasks:

  blobfs.init
  docker.airflow-db-init
  docker.airflow-run
  docker.airflow-web-passwd-init
  docker.exec-shell
  docker.image-build-ds
  docker.image-build-kafka
  docker.image-build-zookeeper
  docker.image-list
  docker.image-rm
  docker.jupyter-rm
  docker.jupyter-run
  docker.jupyter-shell
  docker.kafka-rm
  docker.kafka-run
  docker.machine-create
  docker.machine-install
  docker.machine-rm
  ...
```

## Setup Hosts

hosts.json 을 기반으로 노드 정보를 Master 노드의 /etc/hosts 추가하고 Worker 노드로 복사합니다.

```
./skp.sh host.copy -p="YOUR_PASSWORD"
```

## Setup SSH

암호 없이 키를 통해 클러스터내의 모든 노드에 ssh로 접속하기 위해 개인/공개 인증 키를 생성하고 모든 노드와 교환합니다.

```
./skp.sh ssh.copy-id -p="YOUR_PASSWORD"
```

모든 노드에 원격 명령 수행을 통해 키 복사가 제대로 이루어졌는지 테스트 해봅니다.

```
./skp.sh ssh.cmd -c="ls -al"
```

## Setup Locale

Master 노드에서 설정하였던 Locale 과 동일하게 모든 노드의 언어를 설정합니다.

```
./skp.sh lang.install -l="en_US.UTF-8"
```

설치 후, 콘솔 창이 오작동하는 현상이 있을 경우, 콘솔 창을 닫고 다시 접속하면 됩니다.

## Setup SKP_HOME Share Volume

클러스터에서 모든 노드는 일부 서비스를 위해 노드간 데이터 동기화가 필요한 경우를 위해 같은 SKP_HOME 을 공유합니다.

NFS 사용을 위해 아래 명령을 통해서 nfs 를 각 노드에 설치합니다.

```
./skp.sh nfs.install
```

sudo vi /etc/exports 파일 수정을 통해 nfs 접근 네트워크를 추가합니다. 접근 네트워크는 사용하시는 IP 에 따라 다르게 설정하면 됩니다. 여기서는 노드들이 10.0.x.x 대 IP 를 사용하기에 10.0.0.0/16 으로 설정하였습니다.

공유 디렉토리 경로는 SKP_HOME 과 동일해야 합니다.

```
/home/skp/st-kilda-pier 10.0.0.0/16(rw,insecure,no_root_squash,no_subtree_check,sync)
```

nfs 서버를 재시작 합니다.

```
sudo service nfs-kernel-server restart
```

아래 명령을 통해 Worker 노드에 디렉토리 생성 및 마운트를 해줍니다.

```
./skp.sh nfs.mount-skp
```

아래 명령을 통해서 각 Worker 노드의 마운트가 잘되었는지 체크합니다.

```
./skp.sh ssh.cmd -c="df -h"
```

예)

```
10.0.0.4:/home/skp/st-kilda-pier         252G   11G  229G   5% /home/skp/st-kilda-pier
```

## Setup DFS

SKP 에서는 Spark Cluster에서 사용하기 위한 POSIX 호환 Distributed File System 은 이미 설치되어 있다고 가정합니다.

SKP 가 Public Cloud 에 설치 되어있다면, Public Cloud에서 제공하는 POSIX DFS 서비스(예: AWS EFS, Azure Files)를 제공하기 때문에 해당 서비스의 마운트 포인트가 SKP_DFS를 가르키도록 설정하여 사용하시면 됩니다.

Private 한 환경에서 사용하신다면 오픈소스 형태의 여러 DFS 중 하나를 사용하시면 됩니다.

* MooseFS (https://moosefs.com): 설치 편의성 및 성능 우수
* Ceph
* GlusterFS

DFS 비교: https://en.wikipedia.org/wiki/Comparison_of_distributed_file_systems

env.sh 파일에서 DFS 의 mount 경로를 지정해 줍니다.

```
export SKP_DFS="/mnt/dfs" # Your DFS Path
```

## Setup Docker-Machine

Master 에서 Worker 노드를 편리하게 관리하기 위해 docker-machine 을 설치합니다.

```
./skp.sh docker.machine-install
```

아래 명령으로 모든 노드에 docker-machine을 생성합니다.

```
./skp.sh docker.machine-create
```

이제 Master 에서 Worker 노드를 제어하기 위한 클러스터 설정이 마무리 되었습니다.

## Utils

모든 노드에 같은 원격 명령이 필요할때는 cmd 명령 사용이 가능합니다. 아래는 모든 노드에서 ls -al 명령을 실행하는 예제 입니다.

```
./skp.sh ssh.cmd -c="ls -al"
```
