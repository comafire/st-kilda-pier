#!/bin/bash

IMAGE="skp/docker-zookeeper"
TAG="latest"

docker build --tag $IMAGE:$TAG .
