# Use the Apache Beam SDK base image (Python 3.12)
FROM us-docker.pkg.dev/apache-beam/containers/beam_python3.12_sdk:2.56.0

# Set working directory inside the container
WORKDIR /app

# Copy  ML pipeline code
COPY df_ml_salary_prediction_pipeline.py ./

# Copy custom ML model module (rmi/ml/model.py)
COPY rmi ./rmi

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set entrypoint for Dataflow
ENTRYPOINT ["python", "df_ml_salary_prediction_pipeline.py"]
