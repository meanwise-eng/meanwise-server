FROM meanwise/api-base:latest

ADD awscredentials /root/.aws/credentials
ADD ./code /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["/start.sh"]

CMD ["/usr/local/bin/gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "meanwise_backend.wsgi"]