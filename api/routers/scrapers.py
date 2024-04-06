# FastAPI RestAPI Wrapper to interact with Scrapyd Server using the
# scrapyd-api library. With these endpoints, spiders can be started,
# stopped, and deleted. We can also check the status of running spider
# jobs.

__author__ = 'Chidera'

import logging
from config import config
from fastapi import APIRouter
from scrapyd_api import ScrapydAPI
from fastapi.responses import JSONResponse
from scraper.spiders.base import SpidersEnum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scrapers",
    tags=["scrapers"],
)

scrapy_client = ScrapydAPI(target=config.SCRAPYD_SERVER)


@router.get('/list_spiders')
def list_spiders():
    """
    Returns the list of news article crawlers that exist in the scraper project
    :return: the list of news spiders
    """
    jobs = scrapy_client.list_jobs(project=config.SCRAPYD_PROJECT_NAME)
    spiders = scrapy_client.list_spiders(project=config.SCRAPYD_PROJECT_NAME)

    logger.info("Spider Jobs ", jobs)

    return JSONResponse(
        content={'spiders': [
            {'name': spider,
             'running': True if any(job['spider'] == spider for job in jobs['running']) else False
             } for spider in spiders]},
        status_code=200
    )


@router.get('/{scraper_name}/start')
async def start_scraper(scraper_name: SpidersEnum):
    """
    Starts a spider
    :param scraper_name: name of the spider to be started
    :return: the ID of the started spider job
    """
    spider_name = str(scraper_name)

    jobs = scrapy_client.list_jobs(project=config.SCRAPYD_PROJECT_NAME)
    spiders = scrapy_client.list_spiders(project=config.SCRAPYD_PROJECT_NAME)

    if spider_name in spiders:
        try:
            # check if spider is running
            if any(job['spider'] == spider_name for job in jobs['running']):
                return JSONResponse(content={"message": f"Spider '{scraper_name}' is already running"},
                                    status_code=400)

            # start crawling
            job_id = scrapy_client.schedule(config.SCRAPYD_PROJECT_NAME, scraper_name)
            logger.info(f'Started {spider_name} crawler')

            return JSONResponse(content={"message": f"Spider '{scraper_name}' started successfully",
                                         "job_id": job_id},
                                status_code=200)
        except Exception as e:
            logger.error(f"Error starting spider '{scraper_name}': {e}")
            return JSONResponse(content={"message": f"Error starting spider '{scraper_name}'"}, status_code=500)

    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.get("/{scraper_name}/stop")
async def stop_spider(scraper_name: SpidersEnum):
    """
    Stops a running spider.
    :param scraper_name: name of the spider to stop
    :return: success message
    """
    spider_name = str(scraper_name)

    jobs = scrapy_client.list_jobs(project=config.SCRAPYD_PROJECT_NAME)['running']
    spiders = scrapy_client.list_spiders(project=config.SCRAPYD_PROJECT_NAME)

    if spider_name in spiders:
        for job in jobs:
            if job['spider'] == spider_name:
                try:
                    scrapy_client.cancel(config.SCRAPYD_PROJECT_NAME, job['id'])
                    return JSONResponse(content={"message": f"Spider '{spider_name}' stopped successfully"},
                                        status_code=200)
                except Exception as e:
                    logger.error(f"Error starting spider '{spider_name}': {e}")
                    return JSONResponse(content={"message": f"Error starting spider '{spider_name}'"},
                                        status_code=500)
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not running"}, status_code=400)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.get('/{scraper_name}/status')
async def check_scraper_status(scraper_name: SpidersEnum):
    """
    Checks the status of a running spider
    :param scraper_name: name of the spider
    :return: status message
    """
    spider_name = str(scraper_name)
    result, break_outer = {}, False
    jobs = scrapy_client.list_jobs(project=config.SCRAPYD_PROJECT_NAME)
    spiders = scrapy_client.list_spiders(project=config.SCRAPYD_PROJECT_NAME)

    if spider_name in spiders:
        for job_status, job_data in jobs.items():
            for job in job_data:
                if job['spider'] == spider_name:
                    result['name'] = spider_name
                    result['job_id'] = job.get('id')
                    result['status'] = job_status
                    break_outer = True
                    break
            if break_outer:
                break
        return JSONResponse(content=result, status_code=200)
    else:
        return JSONResponse(content={"message": f"Spider '{scraper_name}' not found"}, status_code=400)


@router.on_event("shutdown")
async def shutdown_event():
    jobs = scrapy_client.list_jobs(project=config.SCRAPYD_PROJECT_NAME)['running']

    for job in jobs:
        scrapy_client.cancel(config.SCRAPYD_PROJECT_NAME, job['id'])
