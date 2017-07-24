FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y python3-pip  locales make

RUN pip3 install --upgrade pip setuptools &&\
	pip3 install sphinx sphinx_rtd_theme

RUN locale-gen en_US.UTF-8
ENV LANG  en_US.UTF-8
ENV LANGUAGE en_US:en

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /docs

