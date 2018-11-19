#!/usr/bin/python

"""This code snippet publishes messages to a Pub/Sub topic in a random fashion."""

from google.cloud import pubsub
import time
import json
import numpy as np
from datetime import datetime
import pytz

publisher = pubsub.PublisherClient()

project_id =  # insert your GCP project id (string) here
topic = 'projects/' + project_id + '/topics/stream_data_ingestion'

locations = ['Helsinki', 'Vantaa', 'Espoo', 'Turku', 'Tampere', 'Jyvaskyla', 'Joensuu', 'Kuopio', 'Kajaani', 'Oulu', 'Rovaniemi']

for i in range(10000):
    timestamp = datetime.now(pytz.timezone('Europe/Helsinki')).strftime('%Y-%m-%d %H:%M:%S')
    location = np.random.choice(locations)
    spend = np.random.randint(1,21)
    message = json.dumps({'timestamp': timestamp,
                          'location': location,
                          'spend': spend})
    print(i, message)
    publisher.publish(topic, message)
    time.sleep(np.random.randint(1,11))
