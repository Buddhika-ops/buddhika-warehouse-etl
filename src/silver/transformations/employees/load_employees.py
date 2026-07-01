from sqlalchemy import text

def upsert_employees(df_silver,engine):
    records =  df_silver.to_dict(orient = "records")
    upsert_query = text("""
        INSERT INTO silver_employees(
            employee_id,
            name,
            department,
            age,
            years_of_experience,
            salary,
            city,
            ingestion_date
        )
        VALUES (
            :employee_id,
            :name,
            :department,
            :age,
            :years_of_experience,
            :salary,
            :city,
            :ingestion_date
        )
        ON CONFLICT (employee_id)
        DO UPDATE SET
            name                = EXCLUDED.name,
            department          = EXCLUDED.department,
            age                 = EXCLUDED.age,
            years_of_experience = EXCLUDED.years_of_experience,
            salary              = EXCLUDED.salary,
            city                = EXCLUDED.city,
            ingestion_date      = EXCLUDED.ingestion_date
        """)
    
    with engine.begin() as connection:
        connection.execute(upsert_query,records)