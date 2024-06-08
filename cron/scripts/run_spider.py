import requests
import pendulum
from http import HTTPStatus

SCRAPERS = ["FoxNewsSpider", "CNNSpider", "NPRNewsSpider", "PoliticoSpider"]
URL = 'http://localhost:9000/scrapers'


def schedule_scrapers():
    for spider in SCRAPERS:
        # check if spider is running
        spider_status = requests.get(f'{URL}/{spider}/status').json()

        # if spider is running, continue to the next spider
        if 'status' in spider_status and spider_status['status'] is True:
            continue
        # else start it
        start_spider = requests.get(f'{URL}/{spider}/start')

        # assert that request was successful
        assert start_spider.status_code == HTTPStatus.OK
