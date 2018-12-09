St. Kilda Pier (이하 SKP)를 자체 Server 들을 통해서 구축 할 경우에 필요한 기본 설치 부분을 다룹니다.

운영체제: Ubuntu 16.04 LTS (아직 Nvidia-Docker 에서 Ubuntu 18.04 LTS 를 지원하고 있지 않기때문에 해당 버전을 사용합니다.)

# User

st-kilda-pier 용 계정 skp를 모든 노드에 생성합니다.

```
sudo adduser skp
```

SKP 명령 수행시 sudo 명령을 통해 권한을 업그레이드 하는 경우가 많기 때문에 자동 수행을 위해 암호 없이 사용 가능하도록 설정합니다.

sudo vi /etc/sudoers 파일을 열어서 sudo 권한 사용자가 암호를 넣지 않아도 되도록 NOPASSWD 설정을 추가합니다.

```
%sudo   ALL=(ALL:ALL) NOPASSWD:ALL
```

그리고 skp 사용자를 sudo 그룹에 추가합니다.

```
sudo usermod -aG sudo skp
```

# Locale - Master

지금 부터 새로 생성된 skp 사용자로 Master 노드에 접속하여 설치를 계속 진행합니다.

설치시 시스템 Locale 설정이 되어 있지 않은 경우, 에러가 발생합니다, 각자 원하는 Locale 로 설정해 아래와 같이 Master 노드를 설정해 줍니다, Slave 노드는 추후 명령을 통해 원격 설치를 진행합니다.

```
sudo apt-get update
sudo apt-get install --no-install-recommends -y locales language-pack-en
sudo sed -i -e 's/# {} UTF-8/{} UTF-8/' /etc/locale.gen && sudo locale-gen
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LC_MESSAGES=POSIX
```

# SKP

SKP에서는 시스템 Python 과 Python Invoke, SSH 원격 명령 및 Docker-Machine을 이용해서 설치 및 관리를 진행합니다.

이를 위해 Master 노드에 아래 패키지를 설치합니다.

```
sudo apt-get update
sudo apt-get install -y python-pip sshpass && pip install invoke
```

이제 SKP 를 사용하기 위하여 Master 노드에 소스를 설치합니다.

```
git clone https://github.com/comafire/st-kilda-pier.git
```

## etc

SKP Cluster를 구축위한 설정 파일을 작성합니다.

설정파일 작성에 관한 부분은 [00-etc.md](https://github.com/comafire/st-kilda-pier/blob/master/doc/00-etc.md) 이 페이지를 참조하세요.

## skp.sh

설치된 bin 디렉토리내에 skp.sh.template 파일을 skp.sh 로 복사하고 경로 변수를 상황에 맞게 수정합니다.

```
export SKP_USER="$USER"
export SKP_HOME="$HOME/st-kilda-pier"
export SKP_MNT="$HOME/mnt"
export SKP_HOSTS="$SKP_HOME/etc/hosts.json"
export SKP_IMAGES="$SKP_HOME/etc/images.json"
export SKP_NETWORKS="$SKP_HOME/etc/networks.json"
export SKP_SERVICES="$SKP_HOME/etc/services.json"
export SKP_VOLUMES="$SKP_HOME/etc/volumes.json"

export SKP_SUSER="root"
export SKP_SHOME="/root/skp"
export SKP_SMNT="/root/mnt"
```

설정이 완료된 후에는 ./skp.sh -l 명령을 통해 사용가능한 명령어 셋이 출력되는지 테스트 해봅니다.

```
cd st-kilda-pier/bin
./skp.sh -l

Available tasks:

  ssh.copy-id
  ssh.cmd
  ...
```

# SSH

원격 명령 수행을 위해 암호 없이 키를 통해 클러스터내의 모든 노드에 ssh로 접속하기 위해 개인/공개 인증 키를 생성하고 모든 노드끼리 서로 교환합니다.

```
./skp.sh ssh.copy-id -p="YOUR_PASSWORD"
```

모든 노드에 원격 명령 수행을 통해 키 복사가 제대로 이루어졌는지 테스트 해봅니다.

```
./skp.sh ssh.cmd -c="ls"
```

# Locale - Slaves

Master 노드에서 설정하였던 Locale 과 동일하게 모든 노드의 언어를 설정합니다.

```
./skp.sh lang.install -r="slave" -l="en_US.UTF-8"
```

# Network

SKP Cluster 로 구성된 네트워크는 Master 노드에 2개 네트워크 카드가 설치되어 있고, 이를 통해서 Public 망과 Private 망으로 연결되는 분리된 망에 설치하는 것으로 가정합니다.

```
Public Network <--> Master <---> Private Network <--> Slaves
```

Master의 Public Network와 연결된 이더넷 카드가 eth0 이고, Private Network와 연결된 이더넷 카드가 eth1 이라고 가정 한다면, 아래 명령으로 iptable 설정을 통해서, Private Network 에 연결된 Slaves 노드에서 Public Network 를 통해 외부 서버들과 통신이 가능하게 됩니다.

```
./skp.sh iptable.masquerade -e="eth0"
```

slave 노드에 접속 후에 ping 명령으로 외부 사이트에 접속 가능하다면 올바르게 구성된 것입니다.

# NFS - Master

Service를 위한 Container 가 여러 노드에 존재하는 분산 서비스의 경우 Container들끼리 데이터 공유가 필요하며, 여기서는 NFS 를 사용합니다.

아래 명령으로 NFS Server를 Master 에 설치합니다.

```
./skp.sh nfs.install
```

# FUSE

Service를 위한 Container 가 외부 노드의 저장소와 연동이 필요할 경우 FUSE 를 사용합니다.

아래 명령으로 FUSE를 모든 노드에 설치합니다.

```
./skp.sh fuse.install
```

이제 SKP를 사용하기 위한 기본 설치가 완료되었습니다. 다음 문서를 통해 계속 적인 설치를 진행하시면 됩니다.
