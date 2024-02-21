import re
from typing import Any

import scrapy
from base import BaseSpider
from scrapy.http import Response


class CNNSpider(BaseSpider):
    name = 'CNN Crawl Spider'
    base_url = 'https://edition.cnn.com/'
    redis_key = 'cnn-visited'
    kafka_topic = 'raw-news-data'
    politics_url_pattern = r'https://\w+\.cnn\.com/\d{4}/\d{2}/\d{2}/politics/.*'

    def start_requests(self):
        yield scrapy.Request(url=self.base_url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        if re.match(self.politics_url_pattern, response.url):
            if not self.is_url_visited(response.url):
                # Extract data from the current page
                title = response.css('title::text').get()
                content = response.css('p::text').getall()

                # Send data to Kafka topic
                self.producer.produce(self.kafka_topic, value={'title': title, 'content': content})
                self.producer.flush()

                # Mark url as visited
                self.mark_url_visited(response.url)

                # Follow links to other pages recursively
                for link in response.css('a::attr(href)').getall():
                    yield response.follow(link, callback=self.parse)
