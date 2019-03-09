#!/bin/bash

#Spark Env
cp $SKP_SHOME/volume/etc/spark/spark-env.sh /usr/local/spark/conf/spark-env.sh

pip2 install -r $SKP_SHOME/volume/etc/jupyter/requirements.txt
pip3 install -r $SKP_SHOME/volume/etc/jupyter/requirements.txt

mkdir /root/.jupyter
cp $SKP_SHOME/volume/etc/jupyter/jupyter_notebook_config.py /root/.jupyter/
jupyter contrib nbextension install --user
jupyter nbextensions_configurator enable --user
jupyter nbextension enable tree-filter/index
jupyter nbextension enable toggle_all_line_numbers/main
jupyter nbextension enable toc2/main
# jupyter nbextension enable code_prettify/code_prettify
jupyter nbextension enable codefolding/edit
#jupyter notebook --allow-root
jupyter lab --allow-root
