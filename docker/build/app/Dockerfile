FROM meanwise/api-base:1.0.0

ENV APP_WORKERS 1

VOLUME /app/static

ADD awscredentials /root/.aws/credentials
ADD ./code /app

WORKDIR /app

RUN apt-get update && \
	apt-get install -y python3 python3-pip python3-dev libpq5 libjpeg8 libpq-dev libjpeg-dev ffmpeg && \
	pip install --no-cache-dir -r requirements.txt && \
    apt-get remove --purge -y python3-dev libpq-dev libjpeg-dev && \
    apt-get remove --purge -y $BUILD_PACKAGES && \
    apt-get autoremove -y && \
    apt-get install -y python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 8000

ENTRYPOINT ["/start.sh"]

CMD ["/usr/local/bin/gunicorn", "-w", "${APP_WORKERS}", "-b", "0.0.0.0:8000", "meanwise_backend.wsgi"]