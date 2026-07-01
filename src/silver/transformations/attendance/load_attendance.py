from sqlalchemy import text

def upsert_attendance(df_silver,engine):
    records =  df_silver.to_dict(orient = "records")
    upsert_query = text("""
                    INSERT INTO silver_attendance (
                        employee_id,
                        date,
                        attendance_hours,
                        ingestion_date,
                        attendance_status,
                        overtime
                    )
                    VALUES (
                        :employee_id,
                        :date,
                        :attendance_hours,
                        :ingestion_date,
                        :attendance_status,
                        :overtime
                    )
                    ON CONFLICT (employee_id, date)
                    DO UPDATE SET
                        employee_id     = EXCLUDED.employee_id,
                        date            = EXCLUDED.date,
                        attendance_hours = EXCLUDED.attendance_hours,
                        ingestion_date  = EXCLUDED.ingestion_date,
                        attendance_status = EXCLUDED.attendance_status,
                        overtime        = EXCLUDED.overtime
                """)
    with engine.begin() as connection:
        connection.execute(upsert_query,records)
