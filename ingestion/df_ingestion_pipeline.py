import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions
from apache_beam.io.gcp.bigquery import WriteToBigQuery
from datetime import datetime
from apache_beam.options.pipeline_options import StandardOptions

options = PipelineOptions()
options.view_as(StandardOptions).streaming = True

# Define DoFn to parse Pub/Sub messages

class ParseJobPostingDoFn(beam.DoFn):
    def process(self, element):
        """
        element: raw bytes from Pub/Sub
        """
        try:
            data = json.loads(element.decode('utf-8'))
            parsed = {
                "job_title": data.get("job_title"),
                "posted_date": data.get("posted_date"),
                "salary_min": data.get("salary_min"),
                "salary_max": data.get("salary_max"),
                "company_name": data.get("company_name"),
                "location": data.get("location"),
                "job_description": data.get("job_description"),
                "ingest_timestamp": datetime.utcnow().isoformat()
            }
            yield parsed
        except Exception as e:
            print(f"Failed to parse record: {e}")
            return


# Pipeline entry
def run(argv=None):
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--subscription', required=True, help='Pub/Sub subscription path')
    parser.add_argument('--output_table', required=True, help='BigQuery table to write to')
    parser.add_argument('--temp_location', required=True, help='GCS path for temp files')
    parser.add_argument('--runner', default='DataflowRunner', help='Pipeline runner')
    parser.add_argument('--project', required=True, help='GCP Project ID')
    parser.add_argument('--region', required=True, help='GCP Region')
    args, beam_args = parser.parse_known_args(argv)

    options = PipelineOptions(
        beam_args,
        project=args.project,
        region=args.region,
        temp_location=args.temp_location,
        streaming=True
    )
    options.view_as(StandardOptions).runner = args.runner

    # BigQuery schema
    table_schema = {
        "fields": [
            {"name": "job_title", "type": "STRING", "mode": "REQUIRED"},
            {"name": "posted_date", "type": "TIMESTAMP", "mode": "NULLABLE"},
            {"name": "salary_min", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "salary_max", "type": "FLOAT", "mode": "NULLABLE"},
            {"name": "company_name", "type": "STRING", "mode": "NULLABLE"},
            {"name": "location", "type": "STRING", "mode": "NULLABLE"},
            {"name": "job_description", "type": "STRING", "mode": "NULLABLE"},
            {"name": "ingest_timestamp", "type": "TIMESTAMP", "mode": "NULLABLE"}
        ]
    }

    with beam.Pipeline(options=options) as p:
        (p
         | "ReadFromPubSub" >> beam.io.ReadFromPubSub(subscription=args.subscription)
         | "WindowIntoFixed60s" >> beam.WindowInto(beam.window.FixedWindows(60))
         | "ParseJobPosting" >> beam.ParDo(ParseJobPostingDoFn())
         | "WriteToBigQuery" >> WriteToBigQuery(
                args.output_table,
                schema=table_schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        )

if __name__ == '__main__':
    run()
