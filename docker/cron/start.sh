#!/bin/bash

pip install -r requirements.txt

printenv | grep -v "no_proxy" >> /etc/environment

/usr/bin/python manage.py crontab remove
/usr/bin/python manage.py crontab add

/bin/bash -l -c "$*"