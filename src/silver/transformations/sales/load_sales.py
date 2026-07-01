from sqlalchemy import text
def upsert_sales(df_silver,engine):
    records =  df_silver.to_dict(orient = "records")
    upsert_query = text("""
                INSERT INTO silver_sales (
                    sale_id,
                    employee_id,
                    product,
                    quantity,
                    amount,
                    date,
                    ingestion_date
                )
                VALUES (
                    :sale_id,
                    :employee_id,
                    :product,
                    :quantity,
                    :amount,
                    :date,
                    :ingestion_date
                )
                ON CONFLICT (sale_id)
                DO UPDATE SET
                    employee_id    = EXCLUDED.employee_id,
                    product        = EXCLUDED.product,
                    quantity       = EXCLUDED.quantity,
                    amount         = EXCLUDED.amount,
                    date           = EXCLUDED.date,
                    ingestion_date = EXCLUDED.ingestion_date
            """)
    
    with engine.begin() as connection:
        connection.execute(upsert_query,records)
