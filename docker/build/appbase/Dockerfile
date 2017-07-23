FROM ubuntu:16.04

ENV LANG  en_US.UTF-8
ENV LANGUAGE en_US:en

ADD ./requirements.txt /app/requirements.txt
ADD ./start.sh /start.sh

WORKDIR /app

RUN apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8 && \
    apt-get install -y python3 python3-pip libpq5 libjpeg8 ffmpeg python3-venv && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip3 install --upgrade pip setuptools &&\
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y python3-dev libpq-dev libjpeg-dev && \
    mkdir ~/venv && cd ~/venv && python3 -m venv meanwise && \
    mkdir /var/lib/meanwise && \
    touch /var/lib/meanwise/meanwise.pid && \
    touch /var/lib/meanwise/meanwise.sock && \
    cd /app && pip install --no-cache-dir -r requirements.txt && \
    apt-get remove --purge -y python3-dev libpq-dev libjpeg-dev && \
    apt-get remove --purge -y $BUILD_PACKAGES && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y cron && \
    rm -rf /var/lib/apt/lists/*

ADD ./code /app