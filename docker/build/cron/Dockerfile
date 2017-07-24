FROM meanwise/api-base:1.0.0

ENV APP_WORKERS 1

ADD ./start.sh /start.sh

ADD awscredentials /root/.aws/credentials
ADD ./code /app

WORKDIR /app

RUN apt-get update && \
	apt-get install -y python3-dev libpq-dev libjpeg-dev && \
	pip install --no-cache-dir -r requirements.txt && \
    apt-get remove --purge -y python3-dev libpq-dev libjpeg-dev && \
    apt-get remove --purge -y $BUILD_PACKAGES && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

RUN /usr/bin/python manage.py crontab add

ENTRYPOINT ["/start.sh"]

CMD ["cron", "-f"]