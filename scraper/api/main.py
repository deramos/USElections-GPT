import enum
import importlib
from fastapi import FastAPI
from scrapy import spiderloader
from scrapy.utils.project import get_project_settings
from scraper.scraper.spiders import SpidersEnum

app = FastAPI(version=1.0, description="Scraper APIs")


@app.get('/')
def home():
    return {"message": "Scraper API", "version": "1.0"}


@app.get('/health')
def health():
    return {'status': 'running'}


@app.get('/scrapers/{scraper_name}/start')
def start_scraper(scraper_name: SpidersEnum):
    module_path = f'scraper.scraper.spiders.{scraper_name}'
    module = importlib.import_module(module_path)
    class_name = SpidersEnum.get_class_name(scraper_name)
    spider_class = getattr(module, class_name)


def create_spider_instance(enum_value):
    pass


if __name__ == '__main__':
    create_spider_instance('cnn')

