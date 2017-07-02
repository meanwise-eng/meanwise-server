#!/bin/bash

docker tag meanwise/api:latest 033556216955.dkr.ecr.us-east-1.amazonaws.com/meanwise/api:latest || exit
docker push 033556216955.dkr.ecr.us-east-1.amazonaws.com/meanwise/api:latest