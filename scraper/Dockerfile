FROM python:3.10-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY scraper/requirements.txt requirements.txt

# Cleanup apt cache to reduce image size
RUN apt-get update && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && rm -rf /root/.cache/pip/*

# upgrade pip and install requirements
RUN pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver

# COPY  folders into docker image (will find cleaner alternative)
COPY scraper /app/scraper
COPY dbservices /app/dbservices
COPY config /app/config
COPY logparser_settings.py /app
COPY scrapy.cfg /app
COPY scrapyd.conf /app
COPY scrapydweb_settings_v10.py /app
COPY .env /app

# Copy and replace Scrapyd logparser settings
RUN mkdir -p /var/scrapyd/logs && \
    cp -f logparser_settings.py /usr/local/lib/python3.10/site-packages/logparser/settings.py

# expose project ports
EXPOSE 6800 5000

# set python path
ENV PYTHONPATH="$PYTHONPATH:/app"