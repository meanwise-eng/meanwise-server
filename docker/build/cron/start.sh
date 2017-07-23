#!/bin/bash

printenv | grep -v "no_proxy" >> /etc/environment

/bin/bash -l -c "$*"