# FastAPI RestAPI Wrapper to interact with Scrapyd Server using the
# scrapyd-api library. With these endpoints, spiders can be started,
# stopped, and deleted. We can also check the status of running spider
# jobs.
import http
import logging
from config import config
from scrapyd_api import ScrapydAPI
from fastapi.responses import JSONResponse
from scraper.spiders.base import SpidersEnum
from scraper.soups.cnn import CNNSoup
from fastapi import APIRouter, BackgroundTasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scrapers",
    tags=["scrapers"],
)

scrapy_client = ScrapydAPI(target=config.SCRAPYD_SERVER)
soup_crawlers = {'CNNSpider': CNNSoup}


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
        content={'scrapers': [
            {'name': spider,
             'running': True if any(job['spider'] == spider for job in jobs['running']) else False
             } for spider in spiders]},
        status_code=http.HTTPStatus.OK
    )


@router.get('/{scraper_name}/start')
async def start_scraper(scraper_name: SpidersEnum, background_task: BackgroundTasks):
    """
    Starts a spider
    :param background_task:
    :param scraper_name: name of the spider to be started
    :return: the ID of the started spider job
    """
    spider_name = str(scraper_name)

    if spider_name in soup_crawlers:
        logger.info(f"Found {spider_name} in soup crawlers. Starting scraper")
        crawler = soup_crawlers[spider_name]()
        background_task.add_task(crawler.scrape)

        return JSONResponse(
            content={"message": f"Scraper '{spider_name}' started successfully"},
            status_code=http.HTTPStatus.OK)

    logger.info(f"scraper name: {scraper_name}. Spider name: {spider_name}")

    jobs = scrapy_client.list_jobs(project=config.SCRAPYD_PROJECT_NAME)
    spiders = scrapy_client.list_spiders(project=config.SCRAPYD_PROJECT_NAME)

    if spider_name in spiders:
        try:
            # check if spider is running
            if any(job['spider'] == spider_name for job in jobs['running']):
                return JSONResponse(content={"message": f"Scraper '{scraper_name}' is already running"},
                                    status_code=http.HTTPStatus.BAD_REQUEST)

            # start crawling
            job_id = scrapy_client.schedule(config.SCRAPYD_PROJECT_NAME, scraper_name)
            logger.info(f'Started {spider_name} crawler')

            return JSONResponse(content={"message": f"Scraper '{scraper_name}' started successfully",
                                         "job_id": job_id},
                                status_code=http.HTTPStatus.OK)
        except Exception as e:
            logger.error(f"Error starting Scraper '{scraper_name}': {e}")
            return JSONResponse(content={"message": f"Error starting Scraper '{scraper_name}'"},
                                status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR)

    else:
        return JSONResponse(content={"message": f"Scraper '{scraper_name}' not found"},
                            status_code=http.HTTPStatus.BAD_REQUEST)


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
                    return JSONResponse(content={"message": f"Scraper '{spider_name}' stopped successfully"},
                                        status_code=http.HTTPStatus.OK)
                except Exception as e:
                    logger.error(f"Error starting Scraper '{spider_name}': {e}")
                    return JSONResponse(content={"message": f"Error starting Scraper '{spider_name}'"},
                                        status_code=http.HTTPStatus.INTERNAL_SERVER_ERROR)
        return JSONResponse(content={"message": f"Scraper '{scraper_name}' not running"},
                            status_code=http.HTTPStatus.BAD_REQUEST)
    else:
        return JSONResponse(content={"message": f"Scraper '{scraper_name}' not found"},
                            status_code=http.HTTPStatus.BAD_REQUEST)


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

    job_status = ['pending', 'pending', 'finished']

    if spider_name in spiders:
        for status in job_status:
            job_data = jobs[status]
            if job_data:
                for job in job_data:
                    print(job)
                    if job['spider'] == spider_name:
                        result['name'] = spider_name
                        result['job_id'] = job.get('id')
                        result['status'] = status
                        break_outer = True
                        break
                if break_outer:
                    break
        if result:
            return JSONResponse(content=result, status_code=http.HTTPStatus.OK)
        else:
            return JSONResponse(content={'message': f'Scraper {scraper_name} not running'},
                                status_code=http.HTTPStatus.OK)
    else:
        return JSONResponse(content={"message": f"Scraper '{scraper_name}' not found"},
                            status_code=http.HTTPStatus.BAD_REQUEST)


@router.on_event("shutdown")
async def shutdown_event():
    jobs = scrapy_client.list_jobs(project=config.SCRAPYD_PROJECT_NAME)['running']

    for job in jobs:
        scrapy_client.cancel(config.SCRAPYD_PROJECT_NAME, job['id'])
