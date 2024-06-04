import json
import re
import scrapy
from typing import Any
from config import config
from .base import BaseSpider
from datetime import datetime
from dateutil import parser
from scrapy.http import Response
from scraper.items import NewsItem
from dbservices.mongoservice import MongoService


class FoxNewsSpider(BaseSpider):
    name = 'FoxNewsSpider'
    base_url = 'https://www.foxnews.com/politics/'
    db_collection_name = 'raw-news'
    redis_key = f'foxnews-visited'
    kafka_topic = config.KAFKA_TOPIC
    politics_url_pattern = r'https://www\.foxnews\.com/politics/(?:\w|-)+'

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

        # Check whether the webpage url matches the `politics` regex and published/modified in 2024
        # and self.get_publication_date(response).year in (2024, 2023)
        if re.match(self.politics_url_pattern, response.url):

            # If the url hasn't been visited yet
            if not self.is_url_visited(response.url):

                # Extract data from the current page
                title = response.css('title::text').get()
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
                news_item['source'] = 'Fox News'
                news_item['created_at'] = datetime.utcnow().isoformat()

                # Save to MongoDB database
                MongoService.insert_data(
                    collection_name=self.db_collection_name,
                    data=[dict(news_item)]
                )

                # Mark url as visited
                self.mark_url_visited(response.url)

        # Follow links to other pages recursively
        links = response.css('a::attr(href)').getall()
        with open('base_links.json', 'w') as f:
            json.dump(links, f)

        for link in links:
            if link.startswith('/politics/'):
                yield response.follow(link, callback=self.parse)

    @staticmethod
    def get_publication_date(response):
        pub_date_str = response.css("span.article-date time::text").get().strip()
        pub_datetime = parser.parse(pub_date_str)
        return pub_datetime
