#!/bin/bash

echo $SSHFS_ID
echo $SSHFS_HOST
echo $SSHFS_VOLUME
/root/volume/bin/mount_sshfs.sh $SSHFS_ID $SSHFS_HOST $SSHFS_VOLUME
echo $S3_ACCOUNT
/root/volume/bin/mount_s3.sh $S3_ACCOUNT
/root/volume/bin/mount_blob.sh

PATH_BASE="/root/volume"
FILE_LOG="nginx-skp.log"

mkdir -p $PATH_BASE/logs/nginx

nginx -c $PATH_BASE/etc/nginx/nginx.conf >> $PATH_BASE/logs/$FILE_LOG 2>&1
