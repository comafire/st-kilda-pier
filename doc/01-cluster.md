# Cluster

운영체제: Ubuntu 16.04

클러스터 설정 부분은 어느 정도 수동 설정 부분을 포함하고 있습니다.

## Install Dependencies

SKP에서는 Python Fabric을 이용해서 설치 및 관리를 진행합니다.

현재 Fabric 버전이 2.x 으로 변경되며, 많은 부분의 하위 호환성이 제거되었습니다.

이에, Fabric 2.x 의 안정화시 까지 Fabric 1.x 버전을 사용합니다.

```
sudo apt-get install -y python-pip sshpass
pip install fabric==1.13.1
```

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

Fabric 설치시 시스템 Locale 설정이 되어 있지 않은 경우, 에러가 발생합니다.

각자 원하는 Locale 로 설정해 아래와 같이 모든 노드를 설정해 줍니다.

```
sudo apt-get install -y language-pack-ko; sudo locale-gen ko_KR.UTF-8; sudo dpkg-reconfigure locales
```

시스템 설정을 업데이트 합니다.

```
sudo update-locale LC_ALL=ko_KR.UTF-8 LANG=ko_KR.UTF-8 LC_MESSAGES=POSIX
```

## Install SKP

이제 SKP 를 사용하기 위하여 마스터 노드에 소스를 설치합니다.

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

## Setup SSH

원격으로 각 노드 제어하기 위해 암호 없이 ssh 를 사용할 수 있도록 설정합니다.

sudo vi /etc/ssh/sshd_config 파일을 열어 아래 내용에 대해서 주석을 제거합니다.

```
AuthorizedKeysFile      %h/.ssh/authorized_keys
```

설정 적용을 위해 ssh 서버를 재시작합니다.

```
sudo service ssh restart
```

암호 없이 키를 통해 ssh 에 접속하기 위해 $SKP_HOME/etc/ssh에 개인/공개 인증 키를 생성합니다.

```
./skp.sh ssh_keygen
```

생성된 키를 각 서버와 교환 합니다.

```
./skp.sh --set SKP_PASSWD="YOUR_PASSWORD" ssh_copy_id
```

## Setup Hosts

hosts.json 을 기반으로 각 서버마다 /etc/hosts 설정합니다.

```
./skp.sh etc_hosts
```

## Setup SKP_HOME Share Volume

클러스터에서 모든 노드는 같은 SKP_HOME 을 공유해야 합니다.

여기에서는 NFS 를 사용합니다. 아래 명령을 통해서 nfs 를 각 노드에 설치합니다.

```
./skp.sh nfs_install
```

nfs 공유를 위해 Master 노드의 SKP_HOME 권한을 root의 777로 변경합니다.

```
source env.sh
sudo chown -R root:root $SKP_HOME
sudo chmod 777 $SKP_HOME
```

sudo vi /etc/exports 파일 수정을 통해 nfs 접근 네트워크를 추가합니다. 공유 디렉토리 경로는 SKP_HOME 과 동일해야 합니다.

```
/home/skp/st-kilda-pier 192.168.0.0/24(rw,insecure,no_root_squash,no_subtree_check,sync)
```

nfs 서버를 재시작 합니다.

```
sudo service nfs-kernel-server restart
```

아래 명령을 통해 Worker 노드에 디렉토리 생성 및 마운트를 해줍니다.

```
./skp.sh nfs_mount_skp
```

아래 명령을 통해서 각 Worker 노드의 마운트가 잘되었는지 체크합니다.

```
./skp.sh rcmd --set RCMD="df -h"
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

## Setup Docker Machine

Master 에서 Worker 노드를 편리하게 관리하기 위해 docker-machine 을 설치합니다.

docker-machine 에서 사용하는 port에 대하여 접근을 허용하기 위해 아래 명령으로 모든 노드의 방화벽 설정을 추가 합니다.

```
./skp.sh ufw
```

아래 명령으로 모든 노드에 docker-machine을 설치하고 sudo 없이 docker 명령을 사용할 수 있도록 합니다.

```
source env.sh
./skp.sh docker_machine_install
./skp.sh rcmd --set RCMD="sudo usermod -aG docker $SKP_USER"
```

아래 명령으로 모든 노드에 docker-machine을 생성합니다.

```
./skp.sh docker_machine_create
```

이제 Master 에서 Worker 노드를 제어하기 위한 클러스터 설정이 마무리 되었습니다.

## Utils

모든 노드에 같은 원격 명령이 필요할때는 rcmd 명령 사용이 가능합니다. 아래는 모든 노드에서 ls -al 명령을 실행하는 예제 입니다.

```
./skp.sh rcmd --set RCMD="ls -al"
```
