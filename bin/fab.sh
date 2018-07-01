#!/bin/bash

source ./env.sh

echo $@
fab -f $SKP_HOME/src/fabfile.py "$@"
