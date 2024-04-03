# Using the raw News Articles, extract news summary, Named Entities, and
# sentence-piece vectors to be saved in chromadb
import datetime
import pendulum
from airflow.decorators import dag, task


@dag(dag_id='news-summary',
     description='Summarize news articles and extract named entities for use in RAG',
     start_date=pendulum.datetime(2024, 4, 2),
     catchup=True,
     )
def summary_dag_taskflow():
     pass

