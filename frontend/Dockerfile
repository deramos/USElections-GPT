FROM python:3.9-slim-buster

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY frontend/requirements.txt requirements.txt

# update image and install supervisord
RUN apt-get update && apt-get install -y supervisor && \
    mkdir -p /var/log/supervisor

# Cleanup apt cache to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# upgrade pip and install requirements
RUN pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver

COPY frontend /app/frontend

# expose project ports
EXPOSE 8501

# set python path
ENV PYTHONPATH="$PYTHONPATH:/app"