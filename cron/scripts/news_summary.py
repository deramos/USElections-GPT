import os
from dbservices.redisservice import RedisService
from dbservices.chromaservice import ChromaService
from datetime import datetime, timedelta

redis_client = RedisService.get_client()
chroma_client = ChromaService.get_client()

redis_key = 'scraped-news-count'


def execute_notebook():
    import papermill as pm

    news_count = int(redis_client.get(redis_key)) if redis_client.get(redis_key) is not None else 0

    end_date, start_date = datetime.now(), datetime.now() - timedelta(days=1, minutes=2)
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")

    pm.execute_notebook(
        input_path="/app/notebooks/News-Summary.ipynb",
        output_path="/app/notebooks/News-Summary-Executed.ipynb",
        parameters={"batch_date": {'$gte': start_date_str, '$lte': end_date_str}}
    )

    updated_count = chroma_client.get_collection(os.getenv('DB_NAME')).count()

    # assert that the updated count is greater than the previously saved news_count
    assert updated_count > news_count

    # update news count
    redis_client.set(redis_key, updated_count)


if __name__ == '__main__':
    execute_notebook()
