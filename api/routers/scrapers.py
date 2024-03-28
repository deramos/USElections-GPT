import logging
import os
from fastapi import APIRouter
from scrapy import spiderloader
from scrapy.crawler import CrawlerRunner
from fastapi.responses import JSONResponse
from scrapy.utils.project import get_project_settings
from scraper.spiders.base import SpidersEnum
from pydantic import BaseModel
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scrapers",
    tags=["scrapers"],
)

settings_path = "scraper.settings"
os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_path)
scrapy_settings = get_project_settings()
spider_loader = spiderloader.SpiderLoader(settings=scrapy_settings)

runners = {}  # Dictionary to store CrawlerRunner instances for each spider
lock = asyncio.Lock()  # Asynchronous lock for thread safety


@router.get('/list_spiders')
def list_spiders():
    return {'spiders': spider_loader.list()}


@router.get('/{scraper_name}/start')
async def start_scraper(scraper_name: SpidersEnum):
    spider_name = str(scraper_name)

    if spider_name in spider_loader.list():
        async with lock:
            if spider_name not in runners:
                try:
                    runner = CrawlerRunner(scrapy_settings)
                    runners[spider_name] = runner
                    thread = runner.crawl(spider_name)
                    await thread.addBoth(lambda _: runners.pop(spider_name, None))
                    logger.info(f'Started {spider_name} crawler')
                    return JSONResponse(content={"message": f"Spider '{scraper_name}' started successfully"},
                                        status_code=200)
                except Exception as e:
                    logger.error(f"Error starting spider '{scraper_name}': {e}")
                    return JSONResponse(content={"message": f"Error starting spider '{scraper_name}'"}, status_code=500)
            else:
                return JSONResponse(content={"message": f"Spider '{scraper_name}' is already running"}, status_code=400)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.get("/{scraper_name}/stop")
async def stop_spider(scraper_name: SpidersEnum):
    spider_name = str(scraper_name)

    if spider_name in spider_loader.list():
        async with lock:
            if spider_name in runners:
                runner = runners[spider_name]
                if runner.crawler.crawling:
                    try:
                        runner.crawler.engine.close_spider(runner.crawler.spider, reason='Stopped from API')
                        logger.info(f"Spider '{scraper_name}' stopped successfully")
                        return JSONResponse(content={"message": f"Spider '{scraper_name}' stopped successfully"},
                                            status_code=200)
                    except Exception as e:
                        logger.error(f"Error stopping spider '{scraper_name}': {e}")
                        return JSONResponse(content={"message": f"Error stopping spider '{scraper_name}'"},
                                            status_code=500)
                else:
                    del runners[spider_name]
                    return JSONResponse(content={"message": f"Spider '{scraper_name}' not running"}, status_code=400)
            else:
                return JSONResponse(content={"message": f"Spider '{scraper_name}' not running"}, status_code=400)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.get('/{scraper_name}/status')
async def check_scraper_status(scraper_name: SpidersEnum):
    spider_name = str(scraper_name)

    if spider_name in spider_loader.list():
        async with lock:
            if spider_name in runners:
                runner = runners[spider_name]
                if runner.crawler.crawling and runner.crawler.spider.name == spider_name:
                    status = "running"
                else:
                    status = "not running"
            else:
                status = "not running"
        return JSONResponse(content={"message": f"Spider '{scraper_name}' {status}"}, status_code=200)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.on_event("shutdown")
async def shutdown_event():
    async with lock:
        for runner in runners.values():
            if runner.crawler.crawling:
                runner.crawler.engine.close_spider(runner.crawler.spider, reason='Application shutdown')
