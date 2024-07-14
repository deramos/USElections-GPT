import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from urllib.parse import urljoin
from dbservices.mongoservice import MongoService


class CNNSoup:
    name = 'CNNSoup'
    base_url = 'https://edition.cnn.com/politics/'
    db_collection_name = 'raw-news'
    politics_url_pattern = r'https:\/\/edition\.cnn\.com\/(?:2023|2024)\/\d{2}/\d{2}/politics\/(?:\w|-)+'
    stripped_text = [
        'Cable News Network. A Warner Bros. Discovery Company. All Rights Reserved.CNN Sans ™ & © 2016 Cable News Network.'
    ]

    def __init__(self):
        self.visited_urls = set()

    def scrape(self):
        """
        Start the scraping process
        """
        self.parse(self.base_url)

    def parse(self, url: str) -> None:
        """
        Parse the scraped webpage for processing. The body of the webpage is only passed if it is a
        politics webpage. Insert data into MongoDB and mark url as visited in the cache
        """
        if url in self.visited_urls:
            return

        print(f"Scraping {self.name} article: {url}")

        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check whether the webpage matches the `politics` regex
        if re.match(self.politics_url_pattern, url):
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
                'publication_date': self.get_publication_date(soup),
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
        self.visited_urls.add(url)

        # Follow links to other pages recursively
        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if full_url.startswith('https://edition.cnn.com'):
                self.parse(full_url)

    @staticmethod
    def get_publication_date(soup):
        timestamp_div = soup.find('div', class_='timestamp')
        if timestamp_div:
            pub_timestamp = timestamp_div.text.strip().split('Updated')[-1].strip()
            pub_datetime = parser.parse(pub_timestamp)
            return pub_timestamp
        return None
