FROM apache/airflow:2.9.0

USER root

COPY airflow/requirements.txt requirements.txt

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         vim \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/* \

# upgrade pip and install requirements
RUN pip3 install --upgrade pip &&  \
    pip install -r requirements.txt --use-deprecated=legacy-resolver

USER airflow

# COPY dags and notebooks
COPY airflow/ /opt/airflow
COPY notebooks /opt/airflow