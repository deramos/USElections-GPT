FROM python:3.9-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY requirements.txt requirements.txt


# upgrade pip and install requirements
RUN apt-get update && pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver

# Cleanup apt cache to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && rm -rf /root/.cache/pip/*

COPY scripts /app/scripts
COPY notebooks /app/notebooks
COPY dbservices /app/dbservices
COPY config /app/config
COPY scheduler.py /app
COPY .env /app


# set python path
ENV PYTHONPATH="$PYTHONPATH:/app"