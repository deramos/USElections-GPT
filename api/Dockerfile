# python:3.9-slim-buster
FROM python:3.10.14-bookworm

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY api/requirements.txt requirements.txt

# Cleanup apt cache to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && rm -rf /root/.cache/pip/*

# upgrade pip and install requirements
RUN apt-get update && \
    pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver

# COPY  folders into docker image (rather crude, but eh!)
COPY api /app/api
COPY config /app/config
COPY daos /app/daos
COPY dbservices /app/dbservices
COPY scraper /app/scraper
COPY util /app/util
COPY .env /app

# expose project ports
EXPOSE 9000

# set python path
ENV PYTHONPATH="$PYTHONPATH:/app"