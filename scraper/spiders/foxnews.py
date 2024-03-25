import re
import scrapy
from typing import Any
from config import config
from .base import BaseSpider
from datetime import datetime
from scrapy.http import Response


class FoxNewsSpider(BaseSpider):
    name = 'FoxNews Crawl Spider'
    base_url = 'https://www.foxnews.com/politics/'
    redis_key = 'foxnews-visited'
    kafka_topic = config.KAFKA_TOPIC
    politics_url_pattern = r'https://www\.foxnews\.com/politics/[\w-]+'

    def start_requests(self):
        """
        Start the scraping process
        :return:
        """
        yield scrapy.Request(url=self.base_url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """
        parse the scraped webpage for processing. The body of the webpage is only passed if it is a
        politics webpage.
        :param response: response from the scraped web page
        :param kwargs: additional keyword arguments
        :return:
        """

        # Check whether the webpage url matches the `politics` regex
        if re.match(self.politics_url_pattern, response.url):

            # If the url hasn't been visited yet
            if not self.is_url_visited(response.url):

                # Extract data from the current page
                title = response.css('title::text').get()
                content = response.css('p::text').getall()

                # Send data to Kafka topic
                self.producer.produce(
                    self.kafka_topic,
                    value={'title': title,
                           'content': content,
                           'url': response.url,
                           'created_at': datetime.utcnow().isoformat()})
                self.producer.flush()

                # Mark url as visited
                self.mark_url_visited(response.url)

                # Follow links to other pages recursively
                for link in response.css('a::attr(href)').getall():
                    yield response.follow(link, callback=self.parse)
