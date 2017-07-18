#!/bin/bash

pip install -r requirements.txt

./manage.py collectstatic

/bin/bash -l -c "$*"