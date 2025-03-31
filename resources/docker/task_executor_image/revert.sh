#!/bin/sh
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker image rm `docker image list -aq`
docker image prune -f
docker build -t alpine:python_0.0.1 ./daemon

