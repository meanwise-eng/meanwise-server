FROM meanwise/api-base:1.0.0

ENV APP_WORKERS=1
ENV WORKER_TIMEOUT=120
ENV ENVIRONMENT=production

ADD awscredentials /root/.aws/credentials
ADD ./code /app

WORKDIR /app

RUN apt-get update && \
	apt-get install -y python3-dev libpq-dev libjpeg-dev libcurl4-openssl-dev && \
	pip install --no-cache-dir -r requirements.txt && \
    apt-get remove --purge -y python3-dev libpq-dev libjpeg-dev && \
    apt-get remove --purge -y $BUILD_PACKAGES && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*


RUN ./manage.py collectstatic --noinput && \
	mkdir -p /usr/share/nginx/html/static && \
	mv -v /app/static/* /usr/share/nginx/html/static/


EXPOSE 8000

ADD ./start.sh /start.sh
ENTRYPOINT ["/start.sh"]

VOLUME /usr/share/nginx/html/static

CMD ["/usr/local/bin/gunicorn", "-w", "${APP_WORKERS}", "-b", "0.0.0.0:8000", "-t", "${WORKER_TIMEOUT}", "meanwise_backend.wsgi"]

