#!/bin/bash

echo $SSHFS_ID
echo $SSHFS_HOST
echo $SSHFS_VOLUME
/root/volume/bin/mount_sshfs.sh $SSHFS_ID $SSHFS_HOST $SSHFS_VOLUME
echo $S3_ACCOUNT
/root/volume/bin/mount_s3.sh $S3_ACCOUNT
/root/volume/bin/mount_blob.sh

#Spark Env 
cp /root/volume/etc/spark/spark-env.sh /usr/local/spark/conf/spark-env.sh

pip2 install -r /root/volume/etc/jupyter/requirements.txt >> /root/volume/logs/jupyter.log 2>&1
pip3 install -r /root/volume/etc/jupyter/requirements.txt >> /root/volume/logs/jupyter.log 2>&1

mkdir -p /root/volume/logs
mkdir /root/.jupyter >> /root/volume/logs/jupyter.log 2>&1
cp /root/volume/etc/jupyter/jupyter_notebook_config.py /root/.jupyter/ >> /root/volume/logs/jupyter.log 2>&1
jupyter contrib nbextension install --user >> /root/volume/logs/jupyter.log 2>&1
jupyter nbextensions_configurator enable --user >> /root/volume/logs/jupyter.log 2>&1
jupyter nbextension enable tree-filter/index >> /root/volume/logs/jupyter.log 2>&1
jupyter nbextension enable toggle_all_line_numbers/main >> /root/volume/logs/jupyter.log 2>&1
jupyter nbextension enable toc2/main >> /root/volume/logs/jupyter.log 2>&1
jupyter nbextension enable code_prettify/code_prettify >> /root/volume/logs/jupyter.log 2>&1
jupyter nbextension enable codefolding/edit >> /root/volume/logs/jupyter.log 2>&1
jupyter notebook --allow-root >> /root/volume/logs/jupyter.log 2>&1
