import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from scrapyd_client import ScrapydClient
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scrapers",
    tags=["scrapers"],
)

scrapy_client = ScrapydClient(url=config.SCRAPYD_SERVER)


@router.get('/list_spiders')
def list_spiders():
    jobs = scrapy_client.jobs(project=config.SCRAPYD_PROJECT_NAME)
    spiders = scrapy_client.spiders(project=config.SCRAPYD_PROJECT_NAME)

    return JSONResponse(
        content={'spiders': [
            {'name': spider,
             'running': True if any(job['spider'] == spider for job in jobs) else False
             } for spider in spiders]},
        status_code=200
    )


@router.get('/{scraper_name}/start')
async def start_scraper(scraper_name: SpidersEnum):
    spider_name = str(scraper_name)

    if spider_name in runner.spider_loader.list():
        try:
            # check if spider is running
            if spider_name in runner.crawlers:
                return JSONResponse(content={"message": f"Spider '{scraper_name}' is already running"}, status_code=400)

            # start crawling
            thread = runner.crawl(spider_name)
            await thread.addBoth(lambda _: runners.pop(spider_name, None))
            logger.info(f'Started {spider_name} crawler')

            return JSONResponse(content={"message": f"Spider '{scraper_name}' started successfully"},
                                status_code=200)
        except Exception as e:
            logger.error(f"Error starting spider '{scraper_name}': {e}")
            return JSONResponse(content={"message": f"Error starting spider '{scraper_name}'"}, status_code=500)

    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.get("/{scraper_name}/stop")
async def stop_spider(scraper_name: SpidersEnum):
    spider_name = str(scraper_name)

    if spider_name in runner.spider_loader.list():
        if runner.crawlers.get(spider_name).crawling:
            try:
                crawler = runner.crawlers.get(spider_name)
                crawler.signals.connect(crawler.stop, signal=signals.spider_closed)
                await crawler.stop()
                return JSONResponse(content={"message": f"Spider '{spider_name}' stopped successfully"},
                                    status_code=200)
            except Exception as e:
                logger.error(f"Error starting spider '{spider_name}': {e}")
                return JSONResponse(content={"message": f"Error starting spider '{spider_name}'"},
                                    status_code=500)
        else:
            return JSONResponse(content={"message": f"Spider '{scraper_name}' not running"}, status_code=400)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.get('/{scraper_name}/status')
async def check_scraper_status(scraper_name: SpidersEnum):
    spider_name = str(scraper_name)

    if spider_name in runner.spider_loader.list():
        if runner.crawlers.get(spider_name).crawling:
            status = "running"
        else:
            status = "not running"
        return JSONResponse(content={"message": f"Spider '{scraper_name}' {status}"}, status_code=200)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.on_event("shutdown")
async def shutdown_event():
    for crawler in runner.crawlers:
        if crawler.crawling:
            crawler.signals.connect(crawler.stop, signal=signals.spider_closed)
            await crawler.stop()
