#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"

cp $ROOT_DIR/requirements.txt $ROOT_DIR/docker/build/appbase/requirements.txt || exit
cp $ROOT_DIR/docker/build/app/start.sh $ROOT_DIR/docker/build/appbase/start.sh || exit

docker build $ROOT_DIR/docker/build/appbase/ -t meanwise/api-base:1.0.0