FROM python:3.9-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install --upgrade pip &&  \
    pip install -r requirements.txt
COPY . /app

EXPOSE 8000

ENV PYTHONPATH="$PYTHONPATH:/app"