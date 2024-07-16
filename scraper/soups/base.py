import logging
import re
import time

import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin
from dbservices.redisservice import RedisService
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(level=logging.INFO)


class BaseSoup:

    def __init__(self, use_playwright=False):
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

        self.use_playwright = use_playwright
        self.playwright = None
        self.browser = None
        self.context = None

    def scrape(self):
        """
        Start the scraping process
        """
        raise NotImplementedError

    def _setup_playwright(self):
        self.logger.info("Using playwright...")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )

    def _teardown_playwright(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def _get_page_content(self, url):
        if self.use_playwright:
            page = self.context.new_page()
            try:
                self.logger.info(f"Navigating to {url}")
                page.goto(url, timeout=30000, wait_until="domcontentloaded")

                self.logger.info("Waiting for body to load")
                page.wait_for_selector('body', state='attached', timeout=10000)

                page.wait_for_timeout(2000)

                content = page.content()
                return content
            except PlaywrightTimeoutError:
                self.logger.warning(f"Timeout while loading {url}, returning partial content")
                return page.content()
            finally:
                page.close()
        else:
            response = requests.get(url, timeout=30)
            return response.text

    def _discover_urls(self, url):
        url = self._normalize_url(url)
        self.logger.info(f"Discovering URLs from: {url}")

        try:
            content = self._get_page_content(url)
            soup = BeautifulSoup(content, 'html.parser')

            self.logger.debug(f"First 1000 characters of content: {content[:1000]}")

            for link in soup.find_all('a', href=True):
                full_url = link['href'] if link['href'].startswith('http') else urljoin(self.base_url, link['href'])
                full_url = self._normalize_url(full_url)

                self.logger.debug(f"Discovered URL: {full_url}")

                if re.match(self.politics_url_pattern, full_url) and not self._is_url_visited(
                        full_url) and full_url not in self.urls_to_scrape:
                    self.urls_to_scrape.append(full_url)
                    self.logger.info(f"Added URL to scrape: {full_url}")

            self.logger.info(f"Total URLs to scrape: {len(self.urls_to_scrape)}")

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

    def _is_url_visited(self, url):
        """
        check if a web url has been visited
        :param url: web url to be checked
        :return: bool (true or false)
        """
        if self.redis_key == 'base-spider-topic':
            raise ValueError(f"Redis key cannot be  '{self.redis_key}'. Change it to proceed.")
        return self.redis_client.sismember(self.redis_key, url)

    def _mark_url_visited(self, url):
        """
        mark a web url as visited
        :param url: web url to be marked
        :return: None
        """
        if self.redis_key == 'base-spider-topic':
            raise ValueError(f"Redis key cannot be  '{self.redis_key}'. Change it to proceed.")
        self.redis_client.sadd(self.redis_key, url)

    @staticmethod
    def _normalize_url(url):
        """Remove fragments from the URL"""
        return url.split('#')[0]

    @staticmethod
    def _get_publication_date(soup):
        raise NotImplementedError
