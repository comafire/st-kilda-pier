#!/bin/bash
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock --network=$1 -e HOST_IP=$2 -e ZK=$3 -i -t skp/docker-kafka:latest /bin/bash
