#!/bin/bash

echo $SSHFS_ID
echo $SSHFS_HOST
echo $SSHFS_VOLUME
/root/volume/bin/mount_sshfs.sh $SSHFS_ID $SSHFS_HOST $SSHFS_VOLUME
echo $S3_ACCOUNT
/root/volume/bin/mount_s3.sh $S3_ACCOUNT
/root/volume/bin/mount_blob.sh

pip2 install -r /root/volume/etc/jupyter/requirements.txt >> /root/volume/logs/flask.log 2>&1
pip3 install -r /root/volume/etc/jupyter/requirements.txt >> /root/volume/logs/flask.log 2>&1

mkdir -p /root/volume/logs

PATH_BASE="/root/volume"
FILE_LOG="flask-skp.log"

FLASK_APP=$PATH_BASE/src/backend/run.py FLASK_DEBUG=1 flask run --host=0.0.0.0 >> $PATH_BASE/logs/$FILE_LOG 2>&1

#python3 /root/volume/src/backend/run.py
