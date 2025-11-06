# GCP Data Engineering Project: "Job Salary Pipelines"

This project implements a complete data engineering and machine learning workflow on Google Cloud Platform (GCP).
It covers ingestion, transformation (ELT), and salary prediction pipelines using Apache Beam, Dataflow, BigQuery, and Cloud Build / Workflows.

## Project Overview

### Part 1:

Name: Ingestion Pipeline
Description:
This streaming Dataflow pipeline ingests real-time job posting data from a Pub/Sub topic into BigQuery using Apache Beam.

Components:

beam.io.ReadFromPubSub

beam.WindowInto: with 60-second fixed windows

beam.ParDo: for JSON parsing

beam.io.WriteToBigQuery: for loading data into rmi_raw.raw_job_posting

Output Table:
rmi_raw.raw_job_posting

### Part 2:

Name:Enrichment (ELT SQL)
Description: Joins raw_job_posting with min_wage data to compute enhanced features (e.g., average salary).
Output Table: rmi_processed.preprocessed_job_posting

The SQL transformation is triggered via GCP Workflows, which runs a BigQuery job.

### Part 3:

Name:ML Prediction Pipeline
Description: Reads preprocessed data, runs an ML model (predict_salary_of_job) to estimate salary per job title per month.
Ouput: rmi_ml.predicted_salary_per_month

## Tech Stack

#### Google Cloud Platform (GCP)

    Pub/Sub
    Dataflow (Apache Beam)
    BigQuery
    Cloud Build
    Cloud Workflows
    Artifact Registry

#### Python 3.12
#### Apache Beam SDK
#### Pandas

## Setup & Installation

#### Clone the project

git clone https://github.com/ShreyaChavan7/rmi-job-salary-pipeline.git
cd rmi-job-salary-pipeline

#### 1. Ingestion Pipeline

    cd ingestion/
    pip install -r requirements.txt

Running the Dataflow Pipeline on GCP:
python df_ingestion_pipeline.py \
 --runner=DirectRunner \
 --subscription=projects/rmi-data-engineering-project/subscriptions/job-posting-sub \
 --output_table=rmi-data-engineering-project:rmi_raw.raw_job_posting \
 --temp_location=gs://gs://rmi-dataflow-temp-bucket/temp \
 --project=rmi-data-engineering-project \
 --region=asia-south1

Build Docker image:
docker build -t asia-south1-docker.pkg.dev/rmi-data-engineering-project/dataflow/ingestion:v1 -f Dockerfile.ingestion .

Push to Artifact Registry:
docker build -t asia-south1-docker.pkg.dev/rmi-data-engineering-project/dataflow/ingestion:v1 -f Dockerfile.ingestion .

#### 2. ML Prediction Pipeline

cd ml/
pip install -r requirements.txt

Running the Dataflow Pipeline on GCP:
python df_ml_salary_prediction_pipeline.py ^
--runner DataflowRunner ^
--project rmi-data-engineering-project ^
--region=europe-west1 ^
--temp_location gs://rmi-dataflow-temp-bucket/temp ^
--staging_location gs://rmi-dataflow-temp-bucket/staging

Build Docker image:
docker build -t asia-south1-docker.pkg.dev/rmi-data-engineering-project/ml-pipelines/salary-predictor:v1 -f Dockerfile.ml .

Push to Artifact Registry:
docker push asia-south1-docker.pkg.dev/rmi-data-engineering-project/ml-pipelines/salary-predictor:v1

## GCP Deployment Workflow

Cloud Build builds the Docker image.

Artifact Registry stores the container.

Dataflow runs the ingestion and ML pipelines.

BigQuery stores intermediate and final results.

Workflows + Cloud Scheduler automate orchestration.

## Cloud Scheduler Setup

We use Google Cloud Scheduler to automatically trigger the GCP Workflow each week.

### Schedule Details

Time: 10:00 AM every Monday

Time Zone: Asia/Kolkata

Target: GCP Workflow execution

### CRON Expression

0 10 \* \* 1

### Explanation:

0 → minute

10 → hour (10 AM)

 * → any day of month

 * → any month

1 → Monday

### Example Command

gcloud scheduler jobs create http workflow-trigger-job \
 --schedule="0 10 \* \* 1" \
 --uri="https://workflowexecutions.googleapis.com/v1/projects/rmi-data-engineering-project/locations/asia-south1/workflows/data-pipeline/executions" \
 --http-method=POST \
 --oauth-service-account-email=workflow-trigger-sa@rmi-data-engineering-project.iam.gserviceaccount.com

## Notes

1. Ensure Application Default Credentials are set up:
   gcloud auth application-default login
2. Verify Artifact Registry and BigQuery permissions.
3. For Dataflow worker pool issues, switch to another zone (e.g., asia-south1-b).
