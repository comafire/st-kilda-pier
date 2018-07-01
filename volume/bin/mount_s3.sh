#!/bin/bash

if [ -z "$1" ]
then
  echo "S3_ACCOUNT is empty"
  exit 0
fi

S3_ACCOUNT=$1
echo "S3_ACCOUNT=$S3_ACCOUNT"

mkdir -p /root/etc/s3
cp /root/volume/etc/s3/s3-passwd /root/etc/s3/s3-passwd
chmod 600 /root/etc/s3/s3-passwd

mkdir -p /root/mnt/s3
CMD="s3fs $S3_ACCOUNT /root/mnt/s3 -o passwd_file=/root/etc/s3/s3-passwd"
echo $CMD
$CMD
