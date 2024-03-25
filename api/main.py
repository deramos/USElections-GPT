import os
import uvicorn
from fastapi import FastAPI
from scrapy import spiderloader
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders import SpidersEnum

app = FastAPI(version=1.0, description="Scraper APIs")

settings_path = "scraper.settings"  # scraper settings in the docker container
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_path)

scrapy_settings = get_project_settings()
spider_loader = spiderloader.SpiderLoader(settings=scrapy_settings)
process = CrawlerProcess(scrapy_settings)


@app.get('/')
def home():
    return {"message": "Scraper API", "version": "1.0"}


@app.get('/health')
def health():
    return {'status': 'running'}


@app.get('/list_spiders')
def list_spiders():
    return {'spiders': spider_loader.list()}


@app.get('/scrapers/{scraper_name}/start')
async def start_scraper(scraper_name: SpidersEnum):
    # module_path = f'scraperr.scraperr.spiders.{scraper_name}'
    # module = importlib.import_module(module_path)
    # class_name = SpidersEnum.get_class_name(scraper_name)
    # spider_class = getattr(module, class_name)

    print(spider_loader.list())

    if scraper_name in spider_loader.list():
        await process.crawl(scraper_name)
        process.start()
        return {"message": f"Spider '{scraper_name}' started successfully"}
    else:
        return {"message": f"Spider '{scraper_name}' not found"}


@app.get("/scrapers/{scraper_name}/start")
async def stop_spider(scraper_name: str):
    if scraper_name in spider_loader.list():
        await process.stop()
        return {"message": f"Spider '{scraper_name}' stopped successfully"}
    else:
        return {"message": f"Spider '{scraper_name}' not found"}


if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)
