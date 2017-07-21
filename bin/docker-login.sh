#!/bin/bash

DOCKER_LOGIN=`aws ecr get-login --no-include-email --region us-east-1`

echo $DOCKER_LOGIN | source /dev/stdin