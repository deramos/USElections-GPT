import logging
import re
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from .base import BaseSoup
from dbservices.mongoservice import MongoService

logging.basicConfig(level=logging.INFO)


class CNNSoup(BaseSoup):

    def __init__(self):
        super().__init__(delay_between_requests=5)
        self.name = 'CNNSoup'
        self.base_url = 'https://edition.cnn.com/politics/'
        self.redis_key = 'cnn-visited'
        self.politics_url_pattern = r'https:\/\/edition\.cnn\.com\/(?:2023|2024)\/\d{2}/\d{2}/politics\/(?:\w|-)+'
        self.stripped_text = [
            'Cable News Network. ',
            'A Warner Bros. Discovery Company.',
            'All Rights Reserved.CNN Sans ™ & © 2016 Cable News Network.'
        ]

    def scrape(self):
        """
        Start the scraping process
        """
        self._discover_urls(self.base_url)
        self.logger.info(f"Processing news URLs; length: {len(self.urls_to_scrape)}")
        self._process_urls()

    def _parse(self, url: str) -> None:
        """
        Parse the scraped webpage for processing. The body of the webpage is only passed if it is a
        politics webpage. Insert data into MongoDB and mark url as visited in the cache
        """
        url = self._normalize_url(url)

        self.logger.info(f"Scraping {self.name} article: {url}")

        try:
            content = self._get_page_content(url)
            if not content:
                return

            soup = BeautifulSoup(content, 'html.parser')

            # Extract data from the current page
            title = soup.title.text if soup.title else None
            content = ' '.join([p.text for p in soup.find_all('p')])
            content = re.sub(r'\s+', ' ', content).strip()

            # strip stripped_texts from content
            for line in self.stripped_text:
                content = content.lstrip(line)

            # create news item dictionary
            news_item = {
                'title': title,
                'raw_content': content,
                'publication_date': self._get_publication_date(soup),
                'url': url,
                'source': 'CNN',
                'created_at': datetime.utcnow().isoformat()
            }

            # Save to MongoDB database
            MongoService.insert_data(
                collection_name=self.db_collection_name,
                data=[news_item]
            )

            # Mark url as visited
            self._mark_url_visited(url)

            # mark as processed
            self.processed_urls += 1

        except Exception as e:
            self.logger.error(f"Error parsing {url}: {str(e)}")

    @staticmethod
    def _get_publication_date(soup):
        timestamp_div = soup.find('div', class_='timestamp')
        if timestamp_div:
            pub_timestamp = timestamp_div.text.strip()
            # Remove any 'Updated' or 'Published' prefix
            pub_timestamp = re.sub(r'^(Updated|Published)\s*', '', pub_timestamp)
            try:
                pub_datetime = parser.parse(pub_timestamp, fuzzy=True)
                return pub_datetime
            except parser.ParserError:
                logging.error(f"Unable to parse date string: {pub_timestamp}")
                return None
        return None