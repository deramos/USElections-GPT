import re
import scrapy
from typing import Any
from config import config
from .base import BaseSpider
from datetime import datetime
from scrapy.http import Response
from scraper.items import NewsItem
from dbservices.mongoservice import MongoService


class PoliticoSpider(BaseSpider):
    name = 'PoliticoSpider'
    base_url = 'https://www.politico.com/'
    db_collection_name = 'raw-news'
    redis_key = f'politico-visited'
    kafka_topic = config.KAFKA_TOPIC
    politics_url_pattern = r'https:\/\/politico\.com\/news\/(?:2024|2023)\/\d{2}\/\d{2}\/(?:\w|-)+-\d+'

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
        self.logger.info(f"Scraping {__name__} article: {response.url}")

        # Check whether the webpage url matches the `politics` regex
        if re.match(self.politics_url_pattern, response.url):

            # If the url hasn't been visited yet
            if not self.is_url_visited(response.url):

                # Extract data from the current page
                title = response.css('h2.headline::text').get()
                content = response.css('p::text').getall()

                # Send data to Kafka topic
                # self.producer.produce(self.kafka_topic, ...)
                # self.producer.flush()

                # create scrapy news item object
                news_item = NewsItem()
                news_item['title'] = title
                news_item['raw_content'] = content
                news_item['publication_date'] = self.get_publication_date(response)
                news_item['url'] = response.url
                news_item['source'] = 'Politico'
                news_item['created_at'] = datetime.utcnow().isoformat()

                # Save to MongoDB database
                MongoService.insert_data(
                    collection_name=self.db_collection_name,
                    data=[dict(news_item)]
                )

                # Mark url as visited
                self.mark_url_visited(response.url)

        # Follow links to other pages recursively
        for link in response.css('a::attr(href)').getall():
            if re.match(self.politics_url_pattern, link):
                yield response.follow(link, callback=self.parse)

    @staticmethod
    def get_publication_date(response):
        datetime_string = response.css('time::attr(datetime)').get()

        # Convert the datetime string to a Python datetime object
        if datetime_string:
            datetime_obj = datetime.fromisoformat(datetime_string)
            return datetime_obj

        return None
