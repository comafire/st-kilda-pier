#!/bin/bash

pip2 install -r $SKP_SHOME/volume/etc/jupyter/requirements.txt
pip3 install -r $SKP_SHOME/volume/etc/jupyter/requirements.txt

rm -f $AIRFLOW_HOME/airflow-webserver.*
rm -f $AIRFLOW_HOME/airflow-scheduler.*

nohup airflow scheduler -D &
# nohup airflow scheduler -D >> $AIRFLOW_HOME/airflow-scheduler.log 2>&1 &
airflow webserver -p 8080 >> $AIRFLOW_HOME/airflow-webserver.log 2>&1
