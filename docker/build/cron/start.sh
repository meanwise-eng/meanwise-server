#!/bin/bash

printenv | grep -v "no_proxy" >> /etc/environment
touch /etc/crontab /etc/cron.*/*

/bin/bash -l -c "$*"
