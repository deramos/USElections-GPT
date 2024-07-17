import datetime

import requests
from config import config
from http import HTTPStatus
import logging

SCRAPERS = ["FoxNewsSpider", "CNNSpider", "NPRNewsSpider", "PoliticoSpider"]
URL = f'{config.FASTAPI_ENDPOINT}/scrapers'

logger = logging.getLogger('SCHEDULE SPIDER')
logging.basicConfig(level=logging.INFO)


def schedule_scrapers():
    logger.info(f"Running Spider on {datetime.datetime.now()}")
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
