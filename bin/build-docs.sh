#!/bin/bash

ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../" && pwd )"

docker build -t meanwise/sphinx:latest $ROOT_DIR/docker/build/sphinx/

docker run --rm -it -v $ROOT_DIR/docs/dev-docs:/docs meanwise/sphinx:latest make clean
docker run --rm -it -v $ROOT_DIR/docs/dev-docs:/docs meanwise/sphinx:latest make html

rsync -avz $ROOT_DIR/docs/dev-docs/build/html/ $ROOT_DIR/docker/build/docs/docs

docker build -t meanwise/dev-docs:latest $ROOT_DIR/docker/build/docs/