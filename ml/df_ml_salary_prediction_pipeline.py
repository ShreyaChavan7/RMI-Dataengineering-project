import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from rmi.ml.model import predict_salary_of_job  # pre-defined ML function
import pandas as pd  # type: ignore


class PredictSalaryFn(beam.DoFn):
    def process(self, element):
        (job_title, month), records = element
        df = pd.DataFrame(records)
        prediction = predict_salary_of_job(df)
        yield {
            "job_title": job_title,
            "month": month,
            "predicted_salary": prediction
        }


def run(argv=None):
    pipeline_options = PipelineOptions(
        runner='DataflowRunner',  
        project='rmi-data-engineering-project',
        region='asia-south1',
        temp_location='gs://rmi-dataflow-temp-bucket/temp',
        job_name='ml-salary-prediction-pipeline'
    )

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "Read from BigQuery" >> beam.io.ReadFromBigQuery(
                query="""
                SELECT
                    job_title,
                    DATE_TRUNC(posted_date, MONTH) AS month,
                    min_salary,
                    salary_max
                FROM `rmi-data-engineering-project.job_postings_dataset.preprocessed_job_posting`
                """,
                use_standard_sql=True
            )
            # Create key-value pairs for grouping
            | "Map to KV" >> beam.Map(lambda row: ((row["job_title"], row["month"]), row))
            # Group all records for each (job_title, month)
            | "Group by Job Title and Month" >> beam.GroupByKey()
            # Predict salary
            | "Predict Salary" >> beam.ParDo(PredictSalaryFn())
            # Write results to BigQuery
            | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                table='rmi-data-engineering-project.job_postings_dataset.predicted_salary_per_month',
                schema='job_title:STRING, month:DATE, predicted_salary:FLOAT',
                write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )


if __name__ == "__main__":
    run()
