import pandas as pd # type: ignore

def predict_salary_of_job(data_df: pd.DataFrame) -> float:
    
    # Basic check
    if data_df.empty:
        return 0.0

    # Simple baseline model: 
    # Take the mean of (salary_min, salary_max, and min_salary if present)
    # This simulates a predictive model’s output.
    salary_columns = [col for col in ['salary_min', 'salary_max', 'min_salary'] if col in data_df.columns]

    # Compute average of all salary columns
    mean_salary = data_df[salary_columns].mean().mean()

    # Add a small adjustment based on job title (to make it look more ML-like)
    job_title = data_df["job_title"].iloc[0].lower()
    if "engineer" in job_title:
        mean_salary *= 1.05
    elif "analyst" in job_title:
        mean_salary *= 0.95
    elif "manager" in job_title:
        mean_salary *= 1.10

   
    return round(mean_salary, 2)
