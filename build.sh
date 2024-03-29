#!/bin/bash

export COMPOSE_PROJECT_NAME=meanwisebuild

rsync -az --exclude=.hypothesis --exclude=.ropeproject --exclude=*.pyc --exclude=media --exclude=docker --exclude=.git --exclude=docker-compose*.yml --exclude=build.sh ./ ./docker/build/app/code --delete

docker-compose -f docker-compose.build.yml build

docker tag meanwisebuild_app meanwise/api:latest
docker tag meanwisebuild_celery meanwise/celery:latest
