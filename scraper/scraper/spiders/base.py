import scrapy
from typing import Any
from scrapy.http import Response

from dbservices.redis import RedisService


class BaseSpider(scrapy.Spider):
    name = None
    base_url = None
    redis_topic = 'base-spider-topic'
    politics_url_pattern = ''
    redis_client = RedisService.get_client()

    def is_url_visited(self, url):
        if self.redis_topic == 'base-spider-topic':
            raise NotImplementedError
        return self.redis_client.sismember(self.redis_topic, url)

    def mark_url_visited(self, url):
        if self.redis_topic == 'base-spider-topic':
            raise NotImplementedError
        self.redis_client.sadd(self.redis_topic, url)

    def start_requests(self):
        raise NotImplementedError

    def parse(self, response: Response, **kwargs: Any) -> Any:
        raise NotImplementedError
