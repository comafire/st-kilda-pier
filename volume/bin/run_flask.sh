#!/bin/bash

pip2 install -r $SKP_SHOME/etc/jupyter/requirements.txt
pip3 install -r $SKP_SHOME/etc/jupyter/requirements.txt

#mkdir -p $SKP_SHOME/logs
#FILE_LOG="$SKP_SHOME/logs/flask-skp.log"
#FLASK_APP=$SKP_SHOME/src/backend/run.py FLASK_DEBUG=1 flask run --host=0.0.0.0 >> $FILE_LOG 2>&1
#python3 /root/volume/src/backend/run.py

FLASK_APP=$SKP_SHOME/src/backend/run.py FLASK_DEBUG=1 flask run --host=0.0.0.0
