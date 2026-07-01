import pandas as pd

def remove_salary_outliers_iqr(df):
   
    # >>Ensure salary is numeric
    df = df.copy()
    df['salary'] = pd.to_numeric(df['salary'], errors='coerce')

    # >>Remove rows with missing salaries
    df = df.dropna(subset=['salary'])

    # >>Calculate IQR
    q1 = df['salary'].quantile(0.25)
    q3 = df['salary'].quantile(0.75)
    iqr = q3 - q1

    # >>Define bounds
    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    # >>Keep only valid rows
    cleaned_df = df[
        (df['salary'] >= lower_bound) &
        (df['salary'] <= upper_bound)
    ]

    return cleaned_df