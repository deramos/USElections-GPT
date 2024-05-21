# Using the raw News Articles, extract news summary, Named Entities, and
# sentence-piece vectors to be saved in chromadb

import pendulum
from pathlib import Path

import requests
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import get_current_context

SCRAPERS = ["FoxNewsSpider", "CNNSpider", "NPRNewsSpider", "PoliticoSpider"]
URL = 'http://localhost:9000/scrapers'


def schedule_scrapers():
    for spider in SCRAPERS:
        # check if spider is running
        spider_status = requests.post(f'{URL}/{spider}/status')

def execute_notebook():
    import papermill as pm

    pm.execute_notebook(
        input_path=Path.joinpath(Path(__file__).parents[2], "notebooks/News Summary.ipynb"),
        output_path=Path.joinpath(Path(__file__).parents[2], "notebooks/News-Summary-Executed.ipynb"),
        parameters={"batch_date": {'$gte': start_date_str, '$lte': end_date_str}}
    )


with DAG(
        dag_id="news-summary",
        description='Summarize news articles and extract named entities for use in RAG',
        start_date=pendulum.datetime(2024, 4, 28),
        catchup=True,
        schedule_interval='@daily'
) as dag:
    """
    Summarize news article, extract named entities, and vectorize the text to be saved into chromadb.
    This is done by running a jupyter notebook `News Summary.ipnb` located in ../notebooks using Papermill
    https://papermill.readthedocs.io/en/latest/
    :return:
    """

    context = get_current_context()
    start_date_str = str(context['data_interval_start'])
    end_date_str = str(context['data_interval_end'])

    start = EmptyOperator(task_id='start')

    # execute_notebook = PapermillOperator(
    #     task_id="run_summarize_notebook",
    #     input_nb=Path.joinpath(Path(__file__).parents[2], "notebooks/News Summary.ipynb"),
    #     parameters={"batch_date": {'$gte': start_date_str, '$lte': end_date_str}},
    # )

    execute_notebook = PythonOperator(
        task_id='run_summarize_notebook',
        python_callable=execute_notebook
    )

    document_count_qa = PythonOperator(
        task_id='chromadb_qa',
        python_callable=check_document_count,
    )

    end = EmptyOperator(task_id='end')

    start >> execute_notebook >> document_count_qa >> end
