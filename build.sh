#!/bin/bash

export COMPOSE_PROJECT_NAME=meanwisebuild

rsync -avz --exclude=media --exclude=docker --exclude=.git --exclude=docker-compose*.yml --exclude=build.sh ./ ./docker/build/app/code

docker-compose -f docker-compose.build.yml build

docker tag meanwisebuild_app meanwise/api:latest