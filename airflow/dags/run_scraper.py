# Using the raw News Articles, extract news summary, Named Entities, and
# sentence-piece vectors to be saved in chromadb
import requests
import pendulum
from pathlib import Path
from http import HTTPStatus

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import get_current_context

SCRAPERS = ["FoxNewsSpider", "CNNSpider", "NPRNewsSpider", "PoliticoSpider"]
URL = 'http://localhost:9000/scrapers'


def schedule_scrapers():
    for spider in SCRAPERS:
        # check if spider is running
        spider_status = requests.get(f'{URL}/{spider}/status').json()
        # if spider is running, continue
        if 'status' in spider_status and spider_status['status'] is True:
            continue
        # else start it
        start_spider = requests.get(f'{URL}/{spider}/start')

        # assert that request was successful
        assert start_spider.status_code == HTTPStatus.OK


with DAG(
        dag_id="run-spider",
        description='Schedule and start daily spiders',
        start_date=pendulum.datetime(2024, 4, 28),
        catchup=True,
        schedule_interval='@daily'
) as dag:
    """
    Schedule the news article scrapy spiders using the FastAPI service created in ../../api/routers/scrapers.
    Use the /{scraper_name}/start endpoint to start the spider and assert that the response code is HTTP_200_OK
    :return:
    """

    start = EmptyOperator(task_id='start')

    execute_notebook = PythonOperator(
        task_id='start_spiders',
        python_callable=schedule_scrapers
    )

    end = EmptyOperator(task_id='end')

    start >> execute_notebook >> end
