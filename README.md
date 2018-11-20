# Google Cloud Data Training

This markdown file contains an outline for a data training workshop.

## Prerequisites

For this training you need:

* owner permissions to a GCP project

* a modern web browser

* (optional) [Google Cloud SDK](https://cloud.google.com/sdk/) installed on your laptop

## Lab 1

In this lab we explore the Google Analytics data from a GA demo account.

Products: _Google Analytics_, _Cloud Console_, _BigQuery_, _Cloud Shell_, _Cloud Datalab_, _Data Studio_


1. The GA demo account tracks data from [Google Merchandise Store](https://www.googlemerchandisestore.com/)

2. View the [Google Analytics dashboard](https://analytics.google.com/analytics/web/)

3. Learn more from video tutorials at [Analytics Academy](https://analytics.google.com/analytics/academy/)

4. Open your [Google Cloud Console](https://console.cloud.google.com)
and navigate to BigQuery

5. Explore the UI, find your `google_analytics_sample` dataset and the `ga_sessions_*` tables within

6. See the documentation:

  - [BigQuery Export for Analytics](https://support.google.com/analytics/answer/3437618) (optional)
  - [BigQuery Export schema](https://support.google.com/analytics/answer/3437719)
  - [Standard SQL Reference](https://cloud.google.com/bigquery/docs/reference/standard-sql/)


7. Try out a simple query like
```sql
SELECT fullVisitorId, date, device.deviceCategory, geoNetwork.country
FROM `google_analytics_sample.ga_sessions_201707*`
GROUP BY 1,2,3,4
```

### Exercise

1. Approximately, how many distinct visitors were there on the Google Merchandise Store site in July 2017?

2. How many distinct visitors were there by country? By device category (desktop, mobile, tablet)?

Choose your analytics tool: BigQuery UI, Data Studio, Datalab

#### BigQuery UI

1. Just use the query editor!

#### Data Studio

1. Sign in to Data Studio from [Google Marketing Platform](https://marketingplatform.google.com/about/data-studio/)

2. Open a blank report (and answer the questions)

3. Create a new data source from BigQuery, follow the steps, select "Session level fields" and click "Add to report"

4. Create a date range for July 2017

5. Create a new field `Distinct visitors` with `COUNT_DISTINCT(fullVisitorId)` and place it in a scorecard

6. Create a filter control dimension `Country` and metric `Distinct visitors` (view it in View mode)

7. Create similar filter controls for `Device category`

####  Datalab

1. Open Cloud Console in a new tab and activate Cloud Shell

2. Get help for Cloud Datalab
```
datalab --help
```

3. Enable Compute Engine and Source Repositories APIs
```
gcloud services enable compute.googleapis.com
gcloud services enable sourcerepo.googleapis.com
```

4. Create a new Datalab instance
```
datalab create --zone europe-north1-a --disk-size-gb 20 my-datalab
```

5. Open the Datalab UI in your browser from web preview (change port to 8081)

6. Create a new notebook and make a query
```sql
%%bq query
SELECT ...
FROM `google_analytics_sample.ga_sessions_*` ...
```

7. Explore the documentation notebooks in the `docs` folder

8. View the [general Datalab documendation](http://googledatalab.github.io/pydatalab/) and the [Python reference](https://cloud.google.com/datalab/docs/)

9. Explore the web UI of the "ungit" version control tool

#### Solution

1. Number of distinct visitors
```sql
SELECT COUNT(DISTINCT fullVisitorId) AS number_of_visitors
FROM `google_analytics_sample.ga_sessions_*`
```

2. Visitors by country
```sql
SELECT geoNetwork.country, COUNT(fullVisitorId) AS number_of_visitors
FROM `google_analytics_sample.ga_sessions_201707*`
GROUP BY country ORDER BY number_of_visitors DESC
```

3. Visitors by device category
```sql
SELECT device.deviceCategory, COUNT(fullVisitorId) AS number_of_visitors
FROM `google_analytics_sample.ga_sessions_201707*`
GROUP BY deviceCategory ORDER BY number_of_visitors DESC
```

### Bonus exercise 1

1. Learn about [BigQuery as a data warehouse](https://cloud.google.com/solutions/bigquery-data-warehouse)

### Bonus exercise 2

1. Run queries from [BigQuery cookbook](https://support.google.com/analytics/answer/4419694)

### Datalab clean up

1. Shutdown the notebooks and close the Datalab tabs

2. Go back to Cloud Shell and close the SSH tunnel by `CTRL-C`.

3. View the state of your Datalab instance by
```
datalab list
```

4. Stop the running instance by
```
datalab stop my-datalab
```

## Lab 2

In this lab we
1. run a streaming pipeline from Pub/Sub to BigQuery,
2. run a batch pipeline from BigQuery to Datastore and Storage,
3. schedule the batch pipeline with Composer.

Products: _Cloud Shell_, _Cloud Source Repositories_, _Pub/Sub_, _Cloud Dataflow_, _BigQuery_, _Cloud Datastore_, _Cloud Storage_, _Cloud Composer_

Frameworks: _Apache Beam_, _Apache Airflow_

### Preparations

1. In Cloud Console, navigate to APIs & Services

2. Enable APIs for Pub/Sub and Cloud Dataflow

or, alternatively,

2. Enable APIs from the Cloud Shell command line by
```
gcloud services enable pubsub.googleapis.com
gcloud services enable dataflow.googleapis.com
gcloud services enable composer.googleapis.com
```

3. From Cloud Shell Terminal settings go to Terminal preferences/Keyboard and click Alt is Meta. This is to ensure you can enter characters like [] in the terminal without complications.

### Pub/Sub

1. Open Cloud Shell (preferably in a new tab) and clone this repository
```
git clone https://github.com/qvik/gcp-data-training.git
```

If you want to use your local code editor instead of the Cloud Shell code editor, follow these steps (you will need to have installed Google Cloud SDK locally):

2. Create a repository in Cloud Source Repositories
```
gcloud source repos create gcp-data-training
```

3. In the repository folder, add remote
```
git remote add google https://source.developers.google.com/p/$GOOGLE_CLOUD_PROJECT/r/gcp-data-training
```

4. Push
```
git push google master
```

5. Clone the `gcp-data-training` repository to your laptop by following the instructions in Source Repositories

Back to Cloud Shell, everyone!

6. Create a virtual environment for the publisher by
```
virtualenv --python=/usr/bin/python pubvenv
```

7. Activate it and install the Python client for Pub/Sub
```
source pubvenv/bin/activate
pip install --upgrade google-cloud-pubsub numpy
```

8. Open `publisher.py` in your code editor and fill in the missing code

9. In Cloud Console, navigate to Pub/Sub, create a topic `stream_data_ingestion` and for it a subscription `process_stream_data`

or, alternatively,

9. Create the topic and its subscription from command line
```
gcloud pubsub topics create stream_data_ingestion
gcloud pubsub subscriptions create --topic stream_data_ingestion process_stream_data
```

10. Run `publisher.py`

11. Open a new Cloud Shell tab and pull messages from the subscription to make sure data is flowing
```
gcloud pubsub subscriptions pull --auto-ack \
projects/$GOOGLE_CLOUD_PROJECT/subscriptions/process_stream_data
```

12. Interrupt the Python process `publisher.py` with `CTRL-C`

### Streaming pipeline

1. Open a new Cloud Shell tab and create a virtual environment for the pipeline
```
virtualenv --python=/usr/bin/python beamvenv
```

2. Activate it and install the Apache Beam Python SDK
```
source beamvenv/bin/activate
pip install --upgrade apache-beam[gcp]
```

3. Open `stream_pipeline.py` in your code editor and inspect the different suggestions for pipelines

4. Take a look at the [Apache Beam Programming Guide](https://beam.apache.org/documentation/programming-guide/), the
[Python reference](https://beam.apache.org/releases/pydoc/2.8.0/), and the [examples in GitHub](https://github.com/apache/beam/tree/master/sdks/python/apache_beam/examples)

5. Go to BigQuery console and create a dataset `my_dataset` and an empty table `stream_data` with fields `timestamp: TIMESTAMP, location: STRING, spend: INTEGER`

6. Launch `publisher.py` in another tab (in its virtual environment) and try out different pipelines with DirectRunner
```
python stream_pipeline.py --runner DirectRunner
```

7. Interrupt the Python processes with `CTRL-C`

8. Create a Cloud Storage bucket `<project_id>-dataflow` for Dataflow temp and staging either from the console or from the command line (see `gsutil help`)
```
gsutil mb -l europe-west1 gs://$GOOGLE_CLOUD_PROJECT-dataflow
```

9. Take a look at [Dataflow documentation](https://cloud.google.com/dataflow/service/dataflow-service-desc) and run the pipeline in Dataflow
```
python stream_pipeline.py --runner DataflowRunner
```

10. View the pipeline by navigating to Dataflow in Cloud Console

11. Clean up by stopping the pipeline and the publisher script

### Batch pipeline

1. In Cloud Console, navigate to Datastore and create a database

2. Inspect `batch_pipeline.py` in your code editor and fill in the missing code

3. Run the pipeline to make sure it works (activate `beamvenv` first)
```
python batch_pipeline.py --runner DirectRunner
```


### Cloud Composer

1. In Cloud Console, navigate to Cloud Composer

2. Create an environment named `data-transfer-environment` in `europe-west1` (this takes a while to finish)

3. Take a look at [Cloud Composer documentation](https://cloud.google.com/composer/docs/concepts/features)

4. Create a Cloud Storage bucket for data export
```
gsutil mb -l europe-west1 gs://$GOOGLE_CLOUD_PROJECT-data-export
```

5. Copy the pipeline into storage bucket
```
gsutil cp pipelines/batch_pipeline.py gs://$GOOGLE_CLOUD_PROJECT-dataflow/pipelines/
```

6. Take a look at [Apache Airflow API Reference](http://airflow.apache.org/code.html)

7. Open `scheduler.py` in your code editor and fill in the missing code

8. Once the environment is ready, navigate to the Airflow web UI and explore it

9. Set the Airflow variable
```
gcloud composer environments run data-transfer-environment \
    --location europe-west1 variables -- --set gcp_project $GOOGLE_CLOUD_PROJECT
```

10. Submit your scheduling to Composer by copying `scheduler.py` into the `dags` folder of your Composer environment bucket

11. Run the pipeline manually, if necessary, and inspect the runs in the web UI

12. View the pipeline by navigating to Dataflow in Cloud Console

### Exercise

1. Draw an architecture diagram of the pipelines in Demo 2


### Clean up

1. In Cloud Console, delete the Composer environment and its storage bucket

2. Check that no Dataflow pipelines are running


## Lab 3

In this lab we train a deep neural network TensorFlow model on
Cloud ML Engine. The task is to classify successful marketing phone
calls of a Portuguese banking institution.

Products: _Cloud ML Engine_

Frameworks: _TensorFlow_

### Preparations

1. Enable the Cloud ML Engine API
```
gcloud services enable ml.googleapis.com
```

### Preparing the model

1. Visit the origin of the dataset at [UCI Machine Learning Repository](https://archive.ics.uci.edu/ml/datasets/bank+marketing)

2. For your convenience, the data has been prepared into training and evaluation sets in `mlengine/data`

3. Open the model file `trainer/model.py` in your code editor and examine the objects `CSV_COLUMNS`, `INPUT_COLUMNS`, etc, which encode your data format

4. Take a look at [TensorFlow documentation](https://www.tensorflow.org/guide/estimators) and fill in the missing feature columns in `build_estimator` function

5. Navigate to the repository folder in your Cloud Shell and set the environment variables
```
TRAIN_DATA=$(pwd)/mlengine/data/bank_data_train.csv
EVAL_DATA=$(pwd)/mlengine/data/bank_data_eval.csv
MODEL_DIR=$(pwd)/mlengine/output
```

6. Change directory to `mlengine` and try the training locally
```
gcloud ml-engine local train \
    --module-name trainer.task \
    --package-path trainer/ \
    --job-dir $MODEL_DIR \
    -- \
    --train-files $TRAIN_DATA \
    --eval-files $EVAL_DATA \
    --train-steps 1000 \
    --eval-steps 100
```

### Training the model in ML Engine

1. Set the environment variables
```
BUCKET_NAME=$GOOGLE_CLOUD_PROJECT-mlengine
REGION=europe-west1
```

2. Create a bucket for ML Engine jobs
```
gsutil mb -l $REGION gs://$BUCKET_NAME
```

3. Copy the data into the bucket
```
gsutil cp $TRAIN_DATA $EVAL_DATA gs://$BUCKET_NAME/data/
```

4. Reset the environment variables for data
```
TRAIN_DATA=gs://$BUCKET_NAME/data/bank_data_train.csv
EVAL_DATA=gs://$BUCKET_NAME/data/bank_data_eval.csv
```

5. Set the environment variables for the training job
```
JOB_NAME=bank_marketing_1
OUTPUT_PATH=gs://$BUCKET_NAME/$JOB_NAME
```

6. Run the training job in ML Engine
```
gcloud ml-engine jobs submit training $JOB_NAME \
    --job-dir $OUTPUT_PATH \
    --runtime-version 1.8 \
    --module-name trainer.task \
    --package-path trainer/ \
    --region $REGION \
    -- \
    --train-files $TRAIN_DATA \
    --eval-files $EVAL_DATA \
    --train-steps 10000 \
    --eval-steps 1000 \
    --verbosity DEBUG
```

7. View the job logs in Cloud Shell
```
gcloud ml-engine jobs stream-logs $JOB_NAME
```

or, alternatively,

7. Inspect the training process on TensorBoard (open web preview on port 6006)
```
tensorboard --logdir=$MODEL_DIR
```

### Hyperparameter tuning

1. Learn more about [hyperparameter tuning](https://cloud.google.com/ml-engine/docs/tensorflow/hyperparameter-tuning-overview) (see also [here](https://cloud.google.com/ml-engine/docs/tensorflow/using-hyperparameter-tuning))

2. Open `hptuning_config.yaml` in your code editor and fill in the missing code

3. In the `mlengine` folder, set the environment variables
```
HPTUNING_CONFIG=$(pwd)/hptuning_config.yaml
JOB_NAME=bank_marketing_hptune_1
OUTPUT_PATH=gs://$BUCKET_NAME/$JOB_NAME
```

4. Run training with hyperparameter tuning
```
gcloud ml-engine jobs submit training $JOB_NAME \
    --stream-logs \
    --job-dir $OUTPUT_PATH \
    --runtime-version 1.8 \
    --config $HPTUNING_CONFIG \
    --module-name trainer.task \
    --package-path trainer/ \
    --region $REGION \
    --scale-tier STANDARD_1 \
    -- \
    --train-files $TRAIN_DATA \
    --eval-files $EVAL_DATA \
    --train-steps 10000 \
    --eval-steps 1000 \
    --verbosity DEBUG
```

5. View the job logs in Cloud Shell
```
gcloud ml-engine jobs stream-logs $JOB_NAME
```

or, alternatively,

5. Inspect the training process on TensorBoard (open web preview on port 6006)
```
tensorboard --logdir=$MODEL_DIR
```

### Deployment

1. Set the environment variable
```
MODEL_NAME=bank_marketing
```

2. Create a model in ML Engine
```
gcloud ml-engine models create $MODEL_NAME --regions=$REGION
```

3. Select the job output to use and look up the path to model binaries
```
gsutil ls -r $OUTPUT_PATH/export
```

4. Set the environment variable with the correct value for `<timestamp>`
```
MODEL_BINARIES=$OUTPUT_PATH/export/bank_marketing/<timestamp>/
```

5. Create a version of the model
```
gcloud ml-engine versions create v1 \
    --model $MODEL_NAME \
    --origin $MODEL_BINARIES \
    --runtime-version 1.8
```

6. From the `mlengine` folder, inspect the test instance
```
cat data/test.json
```

7. Get the prediction for the test instance
```
gcloud ml-engine predict \
    --model $MODEL_NAME \
    --version v1 \
    --json-instances \
    data/test.json
```

## The End
