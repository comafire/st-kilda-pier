#!/bin/bash

IMAGE="skp/docker-kafka"
TAG="latest"

docker build --tag $IMAGE:$TAG .
