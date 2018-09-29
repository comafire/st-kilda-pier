from __future__ import with_statement

import os, sys, json, re
from pprint import pprint

# SKP
SKP_HOME = os.environ["SKP_HOME"]
SKP_HOSTS = os.environ["SKP_HOSTS"]
SKP_USER = os.environ["SKP_USER"]
SKP_PUB_ETH = os.environ["SKP_PUB_ETH"]
SKP_DFS = os.environ["SKP_DFS"]
SKP_NET = os.environ["SKP_NET"]

# Registry
REGISTRY_NAME = os.environ["REGISTRY_NAME"]
REGISTRY_VOLUME = os.environ["REGISTRY_VOLUME"]
REGISTRY_IMAGE = os.environ["REGISTRY_IMAGE"]
REGISTRY_TAG = os.environ["REGISTRY_TAG"]

# SSHFS
SSHFS_ID = os.environ["SSHFS_ID"]
SSHFS_HOST = os.environ["SSHFS_HOST"]
SSHFS_VOLUME = os.environ["SSHFS_VOLUME"]

# S3FS
S3_ACCOUNT = os.environ["S3_ACCOUNT"]
S3_ACCESS_ID = os.environ["S3_ACCESS_ID"]
S3_ACCESS_KEY = os.environ["S3_ACCESS_KEY"]

# BLOBFS
BLOB_ACCOUNT_NAME = os.environ["BLOB_ACCOUNT_NAME"]
BLOB_ACCOUNT_KEY = os.environ["BLOB_ACCOUNT_KEY"]
BLOB_CONTAINER_NAME = os.environ["BLOB_CONTAINER_NAME"]

# Jupyter
JUPYTER_NAME = os.environ["JUPYTER_NAME"]
JUPYTER_PORT = os.environ["JUPYTER_PORT"]
JUPYTER_VOLUME = os.environ["JUPYTER_VOLUME"]
JUPYTER_PASSWORD = os.environ["JUPYTER_PASSWORD"]
JUPYTER_BASEURL = os.environ["JUPYTER_BASEURL"]
JUPYTER_RESTAPIPORT = os.environ["JUPYTER_RESTAPIPORT"]
JUPYTER_IMAGE = os.environ["JUPYTER_IMAGE"]
JUPYTER_TAG = os.environ["JUPYTER_TAG"]
JUPYTER_GPU_IMAGE = os.environ["JUPYTER_GPU_IMAGE"]
JUPYTER_GPU_TAG = os.environ["JUPYTER_GPU_TAG"]
JUPYTER_GPU = os.environ["JUPYTER_GPU"]

# Spark
SPARK_MNAME = os.environ["SPARK_MNAME"]
SPARK_WNAME = os.environ["SPARK_WNAME"]
SPARK_MPORT = os.environ["SPARK_MPORT"]
SPARK_VOLUME = os.environ["SPARK_VOLUME"]
SPARK_URL = os.environ["SPARK_URL"]
SPARK_IMAGE = os.environ["SPARK_IMAGE"]
SPARK_TAG = os.environ["SPARK_TAG"]
SPARK_GPU_IMAGE = os.environ["SPARK_GPU_IMAGE"]
SPARK_GPU_TAG = os.environ["SPARK_GPU_TAG"]
SPARK_GPU = os.environ["SPARK_GPU"]

# MySQL
MYSQL_NAME = os.environ["MYSQL_NAME"]
MYSQL_PORT = os.environ["MYSQL_PORT"]
MYSQL_IMAGE = os.environ["MYSQL_IMAGE"]
MYSQL_TAG = os.environ["MYSQL_TAG"]
MYSQL_VOLUME = os.environ["MYSQL_VOLUME"]
MYSQL_ROOT_PASSWORD = os.environ["MYSQL_ROOT_PASSWORD"]

# Airflow
AIRFLOW_NAME = os.environ["AIRFLOW_NAME"]
AIRFLOW_PORT = os.environ["AIRFLOW_PORT"]
AIRFLOW_VOLUME = os.environ["AIRFLOW_VOLUME"]
AIRFLOW_DB = os.environ["AIRFLOW_DB"]
AIRFLOW_DB_USER = os.environ["AIRFLOW_DB_USER"]
AIRFLOW_DB_PASSWORD = os.environ["AIRFLOW_DB_PASSWORD"]
AIRFLOW__CORE__SQL_ALCHEMY_CONN = os.environ["AIRFLOW__CORE__SQL_ALCHEMY_CONN"]
AIRFLOW_IMAGE = os.environ["AIRFLOW_IMAGE"]
AIRFLOW_TAG = os.environ["AIRFLOW_TAG"]
AIRFLOW_GPU_IMAGE = os.environ["AIRFLOW_GPU_IMAGE"]
AIRFLOW_GPU_TAG = os.environ["AIRFLOW_GPU_TAG"]
AIRFLOW_GPU= os.environ["AIRFLOW_GPU"]

# Portainer
PORTAINER_NAME = os.environ["PORTAINER_NAME"]
PORTAINER_PORT = os.environ["PORTAINER_PORT"]

# Zookeeper
ZOOKEEPER_NAME = os.environ["ZOOKEEPER_NAME"]
ZOOKEEPER_VOLUME = os.environ["ZOOKEEPER_VOLUME"]
ZOOKEEPER_IMAGE = os.environ["ZOOKEEPER_IMAGE"]
ZOOKEEPER_TAG = os.environ["ZOOKEEPER_TAG"]

# Kafka
KAFKA_NAME = os.environ["KAFKA_NAME"]
KAFKA_VOLUME = os.environ["KAFKA_VOLUME"]
KAFKA_IMAGE = os.environ["KAFKA_IMAGE"]
KAFKA_TAG = os.environ["KAFKA_TAG"]

# Flask
FLASK_SECRET = os.environ["FLASK_SECRET"]
FLASK_VOLUME = os.environ["FLASK_VOLUME"]
FLASK_IMAGE = os.environ["FLASK_IMAGE"]
FLASK_TAG = os.environ["FLASK_TAG"]
FLASK_GPU_IMAGE = os.environ["FLASK_GPU_IMAGE"]
FLASK_GPU_TAG = os.environ["FLASK_GPU_TAG"]
FLASK_GPU= os.environ["FLASK_GPU"]

# Nginx
NGINX_VOLUME = os.environ["NGINX_VOLUME"]
NGINX_IMAGE = os.environ["NGINX_IMAGE"]
NGINX_TAG = os.environ["NGINX_TAG"]

hosts = []

with open("/home/skp/st-kilda-pier/etc/hosts.json") as f:
    hosts = json.load(f)
    # pprint(hosts)
