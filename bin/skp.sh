#!/bin/bash

export SKP_USER="$USER"
export SKP_HOME="$HOME/st-kilda-pier"
export SKP_MNT="$HOME/mnt"
export SKP_HOSTS="$SKP_HOME/etc/hosts_single.json"
export SKP_IMAGES="$SKP_HOME/etc/images.json"
export SKP_NETWORKS="$SKP_HOME/etc/networks.json"
export SKP_SERVICES="$SKP_HOME/etc/services_single.json"
export SKP_VOLUMES="$SKP_HOME/etc/volumes_single.json"

export SKP_SUSER="root"
export SKP_SHOME="/root/skp"
export SKP_SMNT="/root/mnt"

#echo $@
invoke -e -r $SKP_HOME/src/tasks "$@"
