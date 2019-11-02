FROM python:3.7

RUN pip install python-telegram-bot
RUN pip install psycopg2

RUN mkdir /app
ADD . /app
WORKDIR /app

CMD python /app/main.py
