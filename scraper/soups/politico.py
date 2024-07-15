import logging
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from .base import BaseSoup
from dbservices.mongoservice import MongoService

logging.basicConfig(level=logging.INFO)


class PoliticoSoup(BaseSoup):

    def __init__(self):
        super().__init__()
        self.name = 'PoliticoSoup'
        self.base_url = 'https://www.politico.com/'
        self.redis_key = 'politico-visited'
        self.politics_url_pattern = r'https:\/\/www\.politico\.com\/news\/(?:2024|2023)\/\d{2}\/\d{2}\/(?:\w|-)+-\d+'

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
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract data from the current page
            title = soup.select_one('h2.headline').text.strip() if soup.select_one('h2.headline') else None
            content = ' '.join([p.text for p in soup.select('p')])
            content = re.sub(r'\s+', ' ', content).strip()

            # create news item dictionary
            news_item = {
                'title': title,
                'raw_content': content,
                'publication_date': self._get_publication_date(soup),
                'url': url,
                'source': 'Politico',
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
        time_tag = soup.find('time')
        if time_tag and 'datetime' in time_tag.attrs:
            datetime_string = time_tag['datetime']
            try:
                return datetime.fromisoformat(datetime_string)
            except ValueError:
                logging.error(f"Unable to parse date string: {datetime_string}")
                return None
        return None
