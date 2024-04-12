import re
import scrapy
from typing import Any
from config import config
from .base import BaseSpider
from datetime import datetime
from scrapy.http import Response
from dbservices.mongoservice import MongoService


class CNNSpider(BaseSpider):
    name = 'CNNSpider'
    base_url = 'https://edition.cnn.com/politics/'
    db_collection_name = 'raw-news'
    redis_key = 'cnn-visited'
    kafka_topic = config.KAFKA_TOPIC
    politics_url_pattern = r'https:\/\/edition\.cnn\.com\/2024\/\d{2}/\d{2}/politics\/(?:\w|-)+'
    stripped_text = [
        'Cable News Network. A Warner Bros. Discovery Company. All Rights Reserved.CNN Sans ™ & © 2016 Cable News Network.'
    ]

    def start_requests(self):
        """
        Start the scraping process
        :return: Generator
        """
        yield scrapy.Request(url=self.base_url, callback=self.parse)

    def parse(self, response: Response, **kwargs: Any) -> Any:
        """
        parse the scraped webpage for processing. The body of the webpage is only passed if it is a
        politics webpage. Insert data into MongoDB and mark url as visited in the cache
        :param response: response from the scraped web page
        :param kwargs: additional keyword arguments
        :return: generator
        """

        self.logger.info(f"Scraping {__name__} article: {response.url}")

        # Check whether the webpage matches the `politics` regex
        if re.match(self.politics_url_pattern, response.url):

            # If the url hasn't been visited yet
            if not self.is_url_visited(response.url):
                # Extract data from the current page
                title = response.css('title::text').get()
                content = response.css('p::text').getall()
                content = ''.join(line.strip() for line in content)

                # strip stripped_texts from content
                for line in self.stripped_text:
                    content = content.lstrip(line)

                # Send data to Kafka topic
                # self.producer.produce(self.kafka_topic, ...)
                # self.producer.flush()

                # Save to MongoDB database
                MongoService.insert_data(
                    collection_name=self.db_collection_name,
                    data=[
                        {'title': title,
                         'raw_content': content,
                         'url': response.url,
                         'source': 'CNN',
                         'created_at': datetime.utcnow().isoformat()
                         }]
                )

                # Mark url as visited
                self.mark_url_visited(response.url)

        # Follow links to other pages recursively
        for link in response.css('a::attr(href)').getall():
            yield response.follow(link, callback=self.parse)
