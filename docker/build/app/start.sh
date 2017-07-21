#!/bin/bash

./manage.py collectstatic --noinput

/bin/bash -l -c "$*"