#!/bin/bash

echo "Specify the version:"
read VERSION

echo "Specify label (eg. latest) tag:"
read TAG

if [ $VERSION != "" ]; then
	echo "Pushing version $VERSION"
	docker tag meanwise/dev-docs:latest 033556216955.dkr.ecr.us-east-1.amazonaws.com/dev-docs:$VERSION || exit
	docker push 033556216955.dkr.ecr.us-east-1.amazonaws.com/dev-docs:$VERSION
fi

if [ $TAG != "" ]; then
	echo "Pushing version $TAG"
	docker tag meanwise/dev-docs:latest 033556216955.dkr.ecr.us-east-1.amazonaws.com/dev-docs:$TAG || exit
	docker push 033556216955.dkr.ecr.us-east-1.amazonaws.com/dev-docs:$TAG
fi