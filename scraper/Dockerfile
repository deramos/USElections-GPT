FROM python:3.10-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY scraper/requirements.txt requirements.txt

# upgrade pip and install requirements
RUN apt-get update && \
    apt-get install -y \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 && \
    pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver

# Install Playwright browsers
RUN playwright install chromium

# Cleanup apt cache to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && rm -rf /root/.cache/pip/*

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