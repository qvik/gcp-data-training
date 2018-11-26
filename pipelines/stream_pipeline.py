#!/usr/bin/python
# -*- coding: utf-8 -*-

"""A sample Apache Beam streaming pipeline that reads from Pub/Sub and writes
to BigQuery.
"""

from __future__ import absolute_import
from __future__ import print_function

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from apache_beam.io import WriteToBigQuery, ReadFromPubSub

import os
import argparse
import logging
import json
from datetime import datetime

project_id =  # insert here your project id (string)


def run(argv=None):
    """This function contains the pipeline logic."""

    parser = argparse.ArgumentParser()

    known_args, pipeline_args = parser.parse_known_args(argv)
    pipeline_args.extend([
        '--project=' + project_id,
        '--job_name=streampipeline',
        '--staging_location=gs://' + project_id + '-dataflow/staging',
        '--temp_location=gs://' + project_id + '-dataflow/temp',
        '--region=europe-west1',
        '--streaming',
    ])

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    subscription = 'projects/' + project_id + '/subscriptions/process_stream_data'
    dataset = 'my_dataset'
    table = 'stream_data'

    # General format:
    # (p | 'name of input step' >> InputClass(args)
    #    | 'name of processing step' >> ProcessClass(args)
    #    | 'name of output step' >> OutputClass(args))
    #
    # Test pipeline input
    # (p | '...' >> ReadFromPubSub(subscription=subscription)
    #    | '...' >> beam.ParDo(PrintElement()))
    #
    # Write to BigQuery
    # (p | '...' >> ReadFromPubSub(subscription=subscription)
    #    | '...' >> beam.ParDo(FormatStreamData())
    #    | '...' >> WriteToBigQuery(dataset=dataset, table=table))

    with beam.Pipeline(options=pipeline_options) as p:
        (p | 'stream_data_ingestion' >> ReadFromPubSub(subscription=subscription)
           | '...')


class PrintElement(beam.DoFn):
    def process(self, element):
        print(element)


class FormatStreamData(beam.DoFn):
    def process(self, element):
        data = json.loads(element)
        data['timestamp'] = data['timestamp'] + '+02:00'
        yield data


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
