FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime

ENV PYTHONBUFFERED=1

WORKDIR /app
COPY api/requirements.txt requirements.txt

# Cleanup apt cache to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# upgrade pip and install requirements
RUN apt-get update && \
    pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver

# COPY  folders into docker image (rather crude, but eh!)
COPY api /app
COPY config /app
COPY daos /app
COPY dbservices /app
COPY scraper /app
COPY util /app
COPY .env /app

# expose project ports
EXPOSE 9000

# set python path
ENV PYTHONPATH="$PYTHONPATH:/app"