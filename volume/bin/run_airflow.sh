#!/bin/bash

echo $SSHFS_ID
echo $SSHFS_HOST
echo $SSHFS_VOLUME
/root/volume/bin/mount_sshfs.sh $SSHFS_ID $SSHFS_HOST $SSHFS_VOLUME
echo $S3_ACCOUNT
/root/volume/bin/mount_s3.sh $S3_ACCOUNT
/root/volume/bin/mount_blob.sh

pip2 install -r /root/volume/etc/jupyter/requirements.txt >> /root/volume/logs/airflow.log 2>&1
pip3 install -r /root/volume/etc/jupyter/requirements.txt >> /root/volume/logs/airflow.log 2>&1

rm -f /root/volume/var/airflow/airflow-webserver.*
rm -f /root/volume/var/airflow/airflow-scheduler.*

mkdir -p /root/volume/logs

#nohup airflow scheduler -D &
nohup airflow scheduler -D >> /root/volume/logs/airflow-scheduler.log 2>&1 &
airflow webserver -p 8080 >> /root/volume/logs/airflow.log 2>&1
