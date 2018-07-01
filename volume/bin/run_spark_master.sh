#!/bin/bash

/root/volume/bin/mount_sshfs.sh $SSHFS_ID $SSHFS_HOST $SSHFS_VOLUME
/root/volume/bin/mount_s3.sh $S3_ACCOUNT
/root/volume/bin/mount_blob.sh

cp /root/volume/etc/spark/spark-defaults.conf /usr/local/spark/conf/spark-defaults.conf
cp /root/volume/etc/spark/spark-env.sh /usr/local/spark/conf/spark-env.sh
/usr/local/spark/bin/spark-class org.apache.spark.deploy.master.Master
