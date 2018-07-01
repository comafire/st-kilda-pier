#!/bin/bash

if [ -z "$1" ]
then
  echo "SSHFS_ID is empty"
  exit 0
fi

if [ -z "$2" ]
then
  echo "SSHFS_HOST is empty"
  exit 0
fi

if [ -z "$3" ]
then
  echo "SSHFS_VOLUME is empty"
  exit 0
fi

# mount sshfs
mkdir /root/.ssh
chmod 700 /root/.ssh
cp /root/volume/etc/ssh/config /root/.ssh
cp /root/volume/etc/ssh/id_rsa /root/.ssh
cp /root/volume/etc/ssh/id_rsa.pub /root/.ssh

chmod 600 /root/.ssh/id_rsa
chmod 600 /root/.ssh/id_rsa.pub

SSHFS_ID=$1
SSHFS_HOST=$2
SSHFS_VOLUME=$3
echo "SSHFS_ID=$SSHFS_ID"
echo "SSHFS_HOST=$SSHFS_HOST"
echo "SSHFS_VOLUME=$SSHFS_VOLUME"

mkdir -p /root/mnt/sshfs
#sshfs sshfs@192.168.0.7:/home/sshfs /root/mnt/sshfs -o allow_other
CMD="sshfs $SSHFS_ID@$SSHFS_HOST:$SSHFS_VOLUME /root/mnt/sshfs -o uid=0,gid=0 "
echo $CMD
$CMD
