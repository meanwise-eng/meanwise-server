#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"

cp $ROOT_DIR/requirements.txt $ROOT_DIR/docker/build/appbase/requirements.txt || exit
cp $ROOT_DIR/docker/build/app/start.sh $ROOT_DIR/docker/build/appbase/start.sh || exit

rsync -avz --exclude=*.pyc --exclude=media --exclude=docker --exclude=.git --exclude=docker-compose*.yml --exclude=build.sh ./ ./docker/build/appbase/code

docker build $ROOT_DIR/docker/build/appbase/ -t meanwise/api-base:1.0.0