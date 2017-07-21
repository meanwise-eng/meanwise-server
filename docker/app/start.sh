#!/bin/bash

pip install -r requirements.txt

./manage.py collectstatic --noinput

/bin/bash -l -c "$*"