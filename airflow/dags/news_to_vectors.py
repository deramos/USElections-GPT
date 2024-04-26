# Using the raw News Articles, extract news summary, Named Entities, and
# sentence-piece vectors to be saved in chromadb
import os
import pendulum
from chromadb import HttpClient
from airflow import DAG
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.operators.python import get_current_context


def check_document_count():
    previous_count: int = Variable.get('vectordb-document-count', 0)

    vectordb_client = HttpClient()
    added_document_count: int = vectordb_client.get_collection('us-election-gpt').count()

    # assert document count is greater than previous count
    assert added_document_count > previous_count

    Variable.set(key='vectordb-document-count', value=previous_count + added_document_count)


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

    execute_notebook = PapermillOperator(
        task_id="run_summarize_notebook",
        input_nb=os.path.join(os.path.dirname(os.path.realpath(__file__)), "notebooks/News Summary.ipynb"),
        parameters={"batch_date": {'$gte': start_date_str, '$lte': end_date_str}},
    )

    document_count_qa = PythonOperator(
        task_id='chromadb_qa',
        python_callable=check_document_count,
    )

    end = EmptyOperator(task_id='end')

    start >> execute_notebook >> document_count_qa >> end
