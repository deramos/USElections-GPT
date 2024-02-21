import re
from typing import Any

import scrapy
from base import BaseSpider
from scrapy.http import Response

from dbservices.redis import RedisService


class CNNSpider(BaseSpider):
    name = 'CNN Crawl Spider'
    base_url = 'https://edition.cnn.com/'
    redis_topic = 'cnn-visited'
    politics_url_pattern = r'https://\w+\.cnn\.com/\d{4}/\d{2}/\d{2}/politics/.*'

    def start_requests(self):
        yield scrapy.Request(url=self.base_url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        if re.match(self.politics_url_pattern, response.url):
            pass
