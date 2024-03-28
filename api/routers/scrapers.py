import os
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scrapy import spiderloader
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scraper.spiders.base import SpidersEnum

router = APIRouter(
    prefix="/scrapers",
    tags=["scrapers"],
)

settings_path = "scraper.settings"  # scraper settings in the docker container
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_path)

scrapy_settings = get_project_settings()
spider_loader = spiderloader.SpiderLoader(settings=scrapy_settings)
runner = CrawlerRunner(scrapy_settings)


@router.get('/list_spiders')
def list_spiders():
    return {'spiders': spider_loader.list()}


@router.post('/{scraper_name}/start')
async def start_scraper(scraper_name: SpidersEnum):
    # module_path = f'scraperr.scraperr.spiders.{scraper_name}'
    # module = importlib.import_module(module_path)
    # spider_name = SpidersEnum.get_class_name(scraper_name)
    # spider_class = getattr(module, class_name)

    if scraper_name in spider_loader.list():
        await runner.crawl(scraper_name)
        return JSONResponse(content={"message": f"Spider '{scraper_name}' started successfully"}, status_code=200)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.post("/{scraper_name}/stop")
async def stop_spider(scraper_name: SpidersEnum):
    if scraper_name in spider_loader.list():
        for task in runner.tasks:
            if task.spider.name == scraper_name:
                task.cancel()
        return JSONResponse(content={"message": f"Spider '{scraper_name}' stopped successfully"}, status_code=200)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)
