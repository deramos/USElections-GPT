import enum
import scrapy
import logging
from typing import Any
from config import config
from scrapy.http import Response
from confluent_kafka import Producer
from dbservices.redisservice import RedisService

logging.basicConfig(level=logging.INFO)


class SpidersEnum(enum.Enum):
    FoxNewsSpider = 'foxnews'
    CNNSpider = 'cnn'
    NPRNewsSpider = 'npr'

    def __str__(self):
        return self.name


class BaseSpider(scrapy.Spider):
    name = None
    base_url = None
    redis_key = 'base-spider-topic'
    politics_url_pattern = ''
    logger = logging.getLogger(__name__)
    redis_client = RedisService.get_client()
    producer = Producer({'bootstrap.servers': config.KAFKA_BROKER})

    def is_url_visited(self, url):
        """
        check if a web url has been visited
        :param url: web url to be checked
        :return: bool (true or false)
        """
        if self.redis_key == 'base-spider-topic':
            raise ValueError(f"Redis key cannot be  '{self.redis_key}'. Change it to proceed.")
        return self.redis_client.sismember(self.redis_key, url)

    def mark_url_visited(self, url):
        """
        mark a web url as visited
        :param url: web url to be marked
        :return: None
        """
        if self.redis_key == 'base-spider-topic':
            raise ValueError(f"Redis key cannot be  '{self.redis_key}'. Change it to proceed.")
        self.redis_client.sadd(self.redis_key, url)

    def start_requests(self) -> Any:
        raise NotImplementedError

    def parse(self, response: Response, **kwargs: Any) -> Any:
        raise NotImplementedError

    @staticmethod
    def get_publication_date(response):
        raise NotImplementedError
