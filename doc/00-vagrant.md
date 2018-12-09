St. Kilda Pier(이하 SKP) 를 Virtual Machine 을 이용하여 가상의 서버들을 구성하여 테스트 구축 할 경우의 기본 설치 부분을 다룹니다.

여러 노드의 서버가 없을 경우, 한대의 성능 좋은 서버에서 Virtual Machine을 여러개 띄워 가상 클러스터를 만들어 봄으로써, SKP의 설치 및 테스트가 가능합니다.

여기서는 Virtual Machine 툴로 VirtualBox 와 Vagrant를 이용해서 SKP 설치를 위한 환경을 구성해 봅니다. (Nvidia GPU 부분은 지원되지 않습니다.)

# User

st-kilda-pier 용 계정 skp를 생성합니다. 여기서는 실제 SKP서비스가 아닌 VirtualBox 및 Vagrant를 설정하고 사용하는 용도로 사용됩니다.

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

# Locale

지금 부터 새로 생성된 skp 사용자로 노드에 접속하여 설치를 계속 진행합니다.

설치시 시스템 Locale 설정이 되어 있지 않은 경우, 에러가 발생합니다, 각자 원하는 Locale 로 설정해 아래와 같이 설정해 줍니다.

```
sudo apt-get update
sudo apt-get install --no-install-recommends -y locales language-pack-en
sudo sed -i -e 's/# {} UTF-8/{} UTF-8/' /etc/locale.gen && sudo locale-gen
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LC_MESSAGES=POSIX
```

# SKP

SKP에서는 시스템 Python 과 Python Invoke, SSH 원격 명령 및 Docker-Machine을 이용해서 설치 및 관리를 진행합니다.

이를 위해 아래 패키지를 설치합니다.

```
sudo apt-get install -y python-pip sshpass && pip install invoke
```

이제 SKP 를 사용하기 위하여 소스를 설치합니다.

```
sudo apt-get install git
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

# VirtualBox & Vagrant

한대의 서버에서 다양한 VM을 올려 테스트 환경 구축을 편리하게 할 수 있는 툴인 VirtualBox 및 Vagrant를 설치합니다.

```
./skp.sh vagrant.install
```

SKP 에서는 cluster 와 single 경우의 VM 생성을 위한 Vagrantfile 을 제공합니다.

* st-kilda-pier/etc/vagrant-file/single
* st-kilda-pier/etc/vagrant-file/cluster

각 디렉토리에서 vagrant 명령을 통해 VM 을 기동할 수 있습니다.

```
cd st-kilda-pier/etc/vagrant-file/single
vagrant up

cd st-kilda-pier/etc/vagrant-file/cluster
vagrant up
```

총 6개의 VM 이 생성되며, 각 VM 은 4 Core, 8GB RAM을 사용하도록 설정되어 있습니다.

* Single VM HostName: s01
* Cluster VMs HostName: c01, c02, c03, c04, c05

서버 성능 상 각 VM 에 대한 성능 조정이 필요하다면 각 디렉토리의 Vagrantfile 에서 vb.cpus, vb.memory 부분을 변경하여 조정 가능합니다.

이제 vagrant ssh 명령을 통해 각 VM 에 접속 가능합니다.

```
cd st-kilda-pier/etc/vagrant-file/cluster
vagrant ssh c01
```

SKP에서 Cluster 키 교환 인증시 SSH 암호 방식 인증을 사용하기 위해 아래와 같이 모든 VM 에 접속하여 암호 방식 인증을 허용해 주고, SSH를 다시 시작합니다.

```
sudo sed -i -e 's/PasswordAuthentication no/PasswordAuthentication yes/g' /etc/ssh/sshd_config
sudo service ssh restart
```

지금 부터는 VM 상에 vagrant 계정으로 접속하여 SKP 를 설치를 진행합니다.

## User

vagrant 는 기본 계정으로 vagrant 를 사용하기 때문에 vagrant 를 이용한 SKP 설치에서는 skp 계정 대신 vagrant 계정을 사용합니다.

각 VM 에서는 기본적으로 st-kilda-pier 디렉토리를 /home/vagrant/st-kilda-pier 디렉토리에 마운트되게 설정되어 있어, SKP 홈디렉토리를 공유하기 위한 NFS 설정이 필요 없습니다.

SKP 명령 수행시 sudo 명령을 통해 권한을 업그레이드 하는 경우가 많기 때문에 자동 수행을 위해 암호 없이 사용 가능하도록 설정합니다.

sudo vi /etc/sudoers 파일을 열어서 sudo 권한 사용자가 암호를 넣지 않아도 되도록 NOPASSWD 설정을 추가합니다.

```
%sudo   ALL=(ALL:ALL) NOPASSWD:ALL
```

그리고 vagrant 사용자를 sudo 그룹에 추가합니다.

```
sudo usermod -aG sudo vagrant
```

usermode 적용을 위해 재접속을 수행합니다.

## Locale

설치시 시스템 Locale 설정이 되어 있지 않은 경우, 에러가 발생합니다, 각자 원하는 Locale 로 설정해 아래와 같이 모든 노드를 설정해 줍니다.

```
sudo apt-get update
sudo apt-get install --no-install-recommends -y locales language-pack-en
sudo sed -i -e 's/# {} UTF-8/{} UTF-8/' /etc/locale.gen && sudo locale-gen
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 LC_MESSAGES=POSIX
```

## sshpass & invoke

SKP에서는 시스템 Python 과 Python Invoke, SSH 원격 명령 및 Docker-Machine을 이용해서 설치 및 관리를 진행합니다.

이를 위해 Master 노드에 아래 패키지를 설치합니다.

```
sudo apt-get update
sudo apt-get install -y python-pip sshpass && pip install invoke
```

## skp.sh

./skp.sh -l 명령을 통해 사용가능한 명령어 셋이 출력되는지 테스트 해봅니다.

```
cd st-kilda-pier/bin
./skp.sh -l

Available tasks:

  ssh.copy-id
  ssh.cmd
  ...
```

## SSH

원격 명령 수행을 위해 암호 없이 키를 통해 클러스터내의 모든 노드에 ssh로 접속하기 위해 개인/공개 인증 키를 생성하고 모든 노드끼리 서로 교환합니다.

```
./skp.sh ssh.copy-id -p="vagrant"
```

모든 노드에 원격 명령 수행을 통해 키 복사가 제대로 이루어졌는지 테스트 해봅니다.

```
./skp.sh ssh.cmd -c="ls"
```

## NFS

Service를 위한 Container 가 여러 노드에 존재하는 분산 서비스의 경우 Container들끼리 데이터 공유가 필요하며, 여기서는 NFS 를 사용합니다.

아래 명령으로 NFS 를 모든 노드에 설치합니다.

```
./skp.sh nfs.install
```

## FUSE

Service를 위한 Container 가 외부 노드의 저장소와 연동이 필요할 경우 FUSE 를 사용합니다.

아래 명령으로 FUSE를 모든 노드에 설치합니다.

```
./skp.sh fuse.install
```
이제 SKP를 VM 상에서 사용하기 위한 기본 설치가 완료되었습니다. 다음 문서를 통해 계속 적인 설치를 진행하시면 됩니다.
