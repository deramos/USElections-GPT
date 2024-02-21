import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Redis Config
REDIS_BROKER_URL = os.getenv("REDIS_BROKER")

# Kafka Config
KAFKA_BROKER = os.getenv('KAFKA_BROKER')
