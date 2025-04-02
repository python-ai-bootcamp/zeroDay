#!/bin/sh
docker container stop task_runner
docker container prune -f
docker container rm --force task_runner
docker image rm alpine:python_task_runner
docker image prune -f
docker build -t alpine:python_task_runner ./resources/docker/task_executor_image
#docker run -t -d --name task_runner alpine:python_task_runner
#docker run -t --name task_runner alpine:python_task_runner # this one messes out stderr and printing it to stdout instead
