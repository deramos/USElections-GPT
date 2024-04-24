import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Redis Config
REDIS_BROKER_URL = os.getenv("REDIS_BROKER")

# ScrapyD Config
SCRAPYD_SERVER = os.getenv("SCRAPYD_SERVER")
SCRAPYD_PROJECT_NAME = 'scraper'

# Kafka Config
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC')

# MongoDB Config
MONGO_URL = os.getenv('MONGO_CONNECTION_STRING')
COLLECTION_NAME = os.getenv('COLLECTION_NAME')

# Model Name
MODEL_NAME = os.getenv('MODEL_NAME')
