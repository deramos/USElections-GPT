import logging
import re
import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
from dbservices.redisservice import RedisService

logging.basicConfig(level=logging.INFO)


class BaseSoup:

    def __init__(self):
        self.name = 'BaseSoup'
        self.base_url = ''
        self.db_collection_name = 'raw-news'
        self.redis_key = 'base-spider-topic'
        self.redis_client = RedisService.get_client()
        self.politics_url_pattern = r''
        self.logger = logging.getLogger(__name__)

        self.max_urls = 30
        self.processed_urls = 0
        self.urls_to_scrape = deque()

    def scrape(self):
        """
        Start the scraping process
        """
        raise NotImplementedError

    def _discover_urls(self, url):
        """
        Discover URLs from the given page and add them to the queue
        """
        url = self.normalize_url(url)

        self.logger.info(f"Discovering URLs from: {url}")

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            for link in soup.find_all('a', href=True):
                full_url = link['href'] if link['href'].startswith('http') else urljoin(self.base_url, link['href'])
                full_url = self.normalize_url(full_url)
                if re.match(self.politics_url_pattern, full_url) and not self.is_url_visited(
                        full_url) and full_url not in self.urls_to_scrape:
                    self.urls_to_scrape.append(full_url)

        except Exception as e:
            self.logger.error(f"Error discovering URLs from {url}: {str(e)}")

    def _process_urls(self):
        """
        Process the discovered URLs
        """
        while self.urls_to_scrape and self.processed_urls <= self.max_urls:
            url = self.urls_to_scrape.popleft()
            self._parse(url)

    def _parse(self, url: str) -> None:
        """
        Parse the scraped webpage for processing. The body of the webpage is only passed if it is a
        politics webpage. Insert data into MongoDB and mark url as visited in the cache
        """
        raise NotImplementedError

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

    @staticmethod
    def normalize_url(url):
        """Remove fragments from the URL"""
        return url.split('#')[0]

    @staticmethod
    def get_publication_date(soup):
        raise NotImplementedError
