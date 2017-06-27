FROM ubuntu:16.04

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev libpq-dev libjpeg-dev ffmpeg python3-venv locales

RUN pip3 install --upgrade pip setuptools &&\
    mkdir ~/venv && cd ~/venv && python3 -m venv meanwise

RUN mkdir /var/lib/meanwise && \
    touch /var/lib/meanwise/meanwise.pid && \
    touch /var/lib/meanwise/meanwise.sock

ADD start.sh /start.sh
ADD awscredentials /root/.aws/credentials

RUN locale-gen en_US.UTF-8
ENV LANG  en_US.UTF-8
ENV LANGUAGE en_US:en

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

EXPOSE 8000

ENTRYPOINT ["/start.sh"]

CMD ["/usr/local/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "meanwise_backend.wsgi"]
