FROM python:3.9-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY scraper/requirements.txt requirements.txt

# Cleanup apt cache to reduce image size
RUN apt-get update && \
    apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# upgrade pip and install requirements
RUN pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver


# Copy and replace Scrapyd logparser settings
RUN mkdir -p /var/scrapyd/logs && \
    cp -f ../../logparser_settings.py /usr/local/lib/python3.9/site-packages/logparser/settings.py

# expose project ports
EXPOSE 6800 5000

# set python path
ENV PYTHONPATH="$PYTHONPATH:/app"