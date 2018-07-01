#!/bin/bash

IMAGE="skp/docker-ds"
TAG="latest"

docker build --tag $IMAGE:$TAG .
