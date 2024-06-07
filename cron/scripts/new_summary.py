from datetime import datetime, timedelta


def execute_notebook():
    import papermill as pm

    end_date, start_date = datetime.now(), datetime.now() - timedelta(days=1, minutes=2)
    end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
    start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")

    pm.execute_notebook(
        input_path="/app/notebooks/News-Summary.ipynb",
        output_path="/app/notebooks/News-Summary-Executed.ipynb",
        parameters={"batch_date": {'$gte': start_date_str, '$lte': end_date_str}}
    )


if __name__ == '__main__':
    execute_notebook()
