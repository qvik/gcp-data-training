#!/usr/bin/python

"""Apache Beam data pipeline from BigQuery to Datastore.

See Apache Beam documentation at https://beam.apache.org/documentation/
and GCP Cloud Dataflow documentation at https://cloud.google.com/dataflow/docs/.
"""

from __future__ import absolute_import

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions

from apache_beam.io import Read, BigQuerySource

from apache_beam.io.gcp.datastore.v1.datastoreio import WriteToDatastore
from google.cloud.proto.datastore.v1 import entity_pb2
from google.cloud.proto.datastore.v1 import query_pb2
from googledatastore import helper as datastore_helper

import os
from datetime import datetime
import argparse
import logging
import uuid

project_id = os.environ['GOOGLE_CLOUD_PROJECT']


def run(argv=None):
    """This function contains the pipeline logic."""

    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)
    # It is preferable to change the job name between runs.
    pipeline_args.extend([
        'project=' + project_id,
        '--job_name=datatransfer' + datetime.now().strftime('%Y%m%d%H%M%S%f'),
    ])

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    # Form an aggregating query.
    query = """
    SELECT
    CURRENT_DATE() AS date,
    EXTRACT(HOUR FROM CURRENT_TIME()) AS hour,
    location,
    SUM(spend) AS total_spend
    FROM `my_dataset.stream_data`
    WHERE EXTRACT(HOUR FROM timestamp) = EXTRACT(HOUR FROM CURRENT_TIME())
    GROUP BY date, hour, location
    """

    # Datastore kind of the entities resulting from the query.
    kind = 'Hourly spend'

    with beam.Pipeline(options=pipeline_options) as p:
        (p | 'Read from BigQuery' >> Read(BigQuerySource(project=project_id,
                                                         query=query,
                                                         use_standard_sql=True))
           | 'Create entity' >> beam.Map(EntityWrapper(kind).make_entity)
           | 'Write to Datastore' >> WriteToDatastore(project_id))


class EntityWrapper(object):
    """Create a Cloud Datastore entity from the given string."""
    def __init__(self, kind):
        self._kind = kind

    def make_entity(self, content):
        """Create entity and set properties."""
        entity = entity_pb2.Entity()
        # We use uuid for keys.
        datastore_helper.add_key_path(entity.key, self._kind, str(uuid.uuid4()))
        datastore_helper.add_properties(entity, content)
        return entity


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
