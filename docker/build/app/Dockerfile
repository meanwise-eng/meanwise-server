FROM meanwise/api-base:latest

ADD ./code /app

WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8000

ENTRYPOINT ["/start.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]