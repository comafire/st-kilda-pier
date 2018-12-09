#!/bin/bash

cp $SKP_SHOME/volume/etc/spark/spark-defaults.conf /usr/local/spark/conf/spark-defaults.conf
cp $SKP_SHOME/volume/etc/spark/spark-env.sh /usr/local/spark/conf/spark-env.sh
/usr/local/spark/bin/spark-class org.apache.spark.deploy.worker.Worker $SPARK_URL
