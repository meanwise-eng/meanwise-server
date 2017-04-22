#!/bin/bash

# Install awscli
#   apt-get install awscli
# Copy the credentials to ~/.aws/credentials
#   cp ../awscredentials ~/.aws/credentials

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

aws s3 sync $DIR/media/ s3://mw-uploads/ --recursive --exclude "*" --include "*.jpg"