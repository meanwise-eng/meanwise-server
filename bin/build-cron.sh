#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"

export COMPOSE_PROJECT_NAME=meanwisebuild

pushd $ROOT_DIR

rsync -avz --exclude=*.pyc --exclude=media --exclude=docker --exclude=.git --exclude=docker-compose*.yml --exclude=build.sh ./ ./docker/build/cron/code

mkdir $ROOT_DIR/docker/build/cron/cron.d
cp $ROOT_DIR/docker/cron/refresh-index $ROOT_DIR/docker/build/cron/cron.d/refresh-index

docker build -t meanwise/cron:latest $ROOT_DIR/docker/build/cron/

rm -rf $ROOT_DIR/docker/build/cron/cron.d
