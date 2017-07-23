#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"

export COMPOSE_PROJECT_NAME=meanwisebuild

pushd $ROOT_DIR

rsync -avz --exclude=*.pyc --exclude=media --exclude=docker --exclude=.git --exclude=docker-compose*.yml --exclude=build.sh ./ ./docker/build/cron/code

docker build -t meanwise/cron:latest $ROOT_DIR/docker/build/cron/
