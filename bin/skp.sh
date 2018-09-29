#!/bin/bash

source ./env.sh

#echo $@
invoke -e -r $SKP_HOME/src/tasks "$@"
