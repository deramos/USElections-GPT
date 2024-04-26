# Using the raw News Articles, extract news summary, Named Entities, and
# sentence-piece vectors to be saved in chromadb
import datetime
import os
import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.decorators import dag, task
from airflow.operators.python import PythonOperator
from airflow.operators.python import get_current_context

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

    execute_notebook = PapermillOperator(
        task_id="run_summarize_notebook",
        input_nb=os.path.join(os.path.dirname(os.path.realpath(__file__)), "notebooks/News Summary.ipynb"),
        parameters={"batch_date": {'$gte': start_date_str, '$lte': end_date_str}},
    )

    execute_notebook
