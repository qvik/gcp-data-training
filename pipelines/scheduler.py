#!/usr/bin/python

"""A simple DAG for scheduling Dataflow runs and data exports from BigQuery.

This Airflow DAG is run daily by Cloud Composer. It runs two operators:
1. A Dataflow pipeline that queries BigQuery and writes into Datastore.
2. A data export operator from BigQuery to Cloud Storage.

Store this file in the `dags` folder of the Cloud Composer environment.

See Apache Airflow documentation at https://airflow.apache.org/index.html
and GCP Cloud Composer documentation at https://cloud.google.com/composer/docs/.
"""

from __future__ import print_function
from __future__ import absolute_import

import datetime
import logging

from airflow import models

from airflow.contrib.operators.bigquery_to_gcs import BigQueryToCloudStorageOperator
from airflow.contrib.operators.dataflow_operator import DataFlowPythonOperator

project_id = models.Variable.get('gcp_project')

default_dag_args = {
    # The start_date describes when a DAG is valid / can be run. Set this to a
    # fixed point in time rather than dynamically, since it is evaluated every
    # time a DAG is parsed. See:
    # https://airflow.apache.org/faq.html#what-s-the-deal-with-start-date
    'start_date': datetime.datetime.now(),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=20),
    'dataflow_default_options': {
               'runner': 'DataflowRunner',
               'project': project_id,
               'region': 'europe-west1',
               'staging_location': 'gs://' + project_id + '-dataflow/staging/',
               'temp_location': 'gs://' + project_id + '-dataflow/temp/'
               }
}

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG(
        'hourly_data_transfer',
        schedule_interval='0 * * * *',
        default_args=default_dag_args) as dag:

    run_dataflow = DataFlowPythonOperator(
        py_file='gs://' + project_id + '-dataflow/pipelines/batch_pipeline.py',
        task_id='run_Dataflow_from_BQ_to_Datastore',
        dataflow_default_options=default_dag_args['dataflow_default_options']
    )

    bq_to_gcs = BigQueryToCloudStorageOperator(
        task_id='export_stream_data_from_BQ',
        source_project_dataset_table='my_dataset.stream_data',
        destination_cloud_storage_uris=['gs://' + project_id + '-data-export/stream_data.csv'],
        export_format='CSV')

    # Define DAG dependencies.
    run_dataflow
    bq_to_gcs
