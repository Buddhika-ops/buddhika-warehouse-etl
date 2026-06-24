import pandas as pd
from sqlalchemy import text
from src.db_engine import get_engine
from datetime import datetime
from utils.logger import get_logger

logger = get_logger()
engine = get_engine()

today = pd.Timestamp.today().normalize()
current_year = datetime.now().year

def clean_silver_employees_table():
    with engine.begin() as connection:
            connection.execute(text("TRUNCATE TABLE silver_employees"))

    logger.info("[SILVER][EMPLOYEES] cleaning started")
    try:
        df = pd.read_sql("SELECT * FROM bronze_employees ",engine)

        # >> to int
        df['employee_id'] = pd.to_numeric(df['employee_id'],errors="coerce")
        df['age'] = pd.to_numeric(df['age'],errors="coerce")
        df['years_of_experience'] = pd.to_numeric(df['years_of_experience'],errors="coerce")
        df['salary'] = pd.to_numeric(df['salary'],errors="coerce")

        # >> to String
        df['name'] = df['name'].str.title()
        df['department'] = df['department'].str.upper()
        df['city'] = df['city'].str.title()

        # >> fix empty departments in employee table
        df['department'] = df['department'].fillna('unknown')
        # >> fix empty ages in employee table
        df['age'] = df['age'].fillna( df['years_of_experience'] + 18)
        # >> fix empty salary with mean of salary in employee table
        df['salary'] = df['salary'].fillna(df['salary'].mean()).astype(int)
        # >> check salary can't be negative
        df = df[df['salary']> 0]

        # >> check years_of_experience > age 
        df = df[(df['years_of_experience'] < df['age']) &
            ( df['age'] - df['years_of_experience'] >= 18) ]
        
        # >> outliers 
        z = (df['salary'] - df['salary'].mean())/ df['salary'].std()
        df = df[z.abs() <= 3 ]

        


        df['join_date_estimated'] = current_year - df['years_of_experience']
        df["ingestion_date"] = pd.Timestamp.now()

        logger.info(f"[SILVER][EMPLOYEES] cleaning completed | rows={len(df)}")


        try:
            df.to_sql("silver_employees",engine,if_exists="append",index=False)

            logger.info(f"[SILVER][EMPLOYEES] load completed | rows={len(df)}")
        except Exception as e:
            logger.error(f"[SILVER][EMPLOYEES] load failed | error={e}")

    except Exception as e:
        logger.error(f"[SILVER][EMPLOYEES] load failed | error={e}")



def load_silver_sales_table():
    logger.info("[SILVER][SALES] cleaning started")
    
    try:
        chunk_size = 50000       
        total = 0

        quary = """
                    SELECT PERCENTILE_CONT(0.5)
                    WITHIN GROUP (ORDER BY amount) AS median_amount
                    FROM bronze_sales
                    WHERE amount IS NOT NULL;
                """

        silver_employee_df = pd.read_sql("SELECT * FROM silver_employees ",engine)
        chunk = pd.read_sql("SELECT * FROM bronze_sales ", engine, chunksize= chunk_size)
        global_amount_median = pd.read_sql(quary,engine)['median_amount'].iloc[0]
        
        for silver_sales_df in chunk:

            silver_sales_df['sale_id'] = pd.to_numeric(silver_sales_df['sale_id'],errors='coerce')
            silver_sales_df['employee_id'] = pd.to_numeric(silver_sales_df['employee_id'],errors='coerce')
            silver_sales_df['amount'] = pd.to_numeric(silver_sales_df['amount'],errors='coerce')
            silver_sales_df['product'] = silver_sales_df['product'].str.title()
            silver_sales_df['date'] = pd.to_datetime(silver_sales_df['date'],errors= 'coerce')


            # >>check sales without employees and flag it
            invalid_mask = ~silver_sales_df["employee_id"].isin(silver_employee_df["employee_id"])
            silver_sales_df['sales_without_employees_flag'] = invalid_mask.astype(bool)
            silver_sales_df.loc[invalid_mask , "employee_id"] = -1


            # >> missing priduct name fill using unknown
            silver_sales_df['product'] = silver_sales_df['product'].fillna("unknown")

        
            # >> missing amount fill using median and flag it.
            silver_sales_df['missing_amount_flag'] = silver_sales_df["amount"].isnull().astype(bool)
            silver_sales_df["amount"] = silver_sales_df["amount"].fillna(global_amount_median)


            silver_sales_df['ingestion_date'] = pd.Timestamp.now()

            logger.info(
                f"[SILVER][SALES] chunk cleaned | rows={len(silver_sales_df)}"
            )

            upsert_query = text(
                """
                    INSERT INTO silver_sales(
                        sale_id,
                        employee_id,
                        product,
                        amount,
                        date,
                        sales_without_employees_flag,
                        missing_amount_flag,
                        ingestion_date 
                    )
                    VALUES(
                        :sale_id,
                        :employee_id,
                        :product,
                        :amount,
                        :date,
                        :sales_without_employees_flag,
                        :missing_amount_flag,
                        :ingestion_date 
                    )
                    ON CONFLICT (sale_id)
                    DO UPDATE SET
                        employee_id = EXCLUDED.employee_id,
                        product = EXCLUDED.product,
                        amount = EXCLUDED.amount,
                        date = EXCLUDED.date,
                        sales_without_employees_flag = EXCLUDED.sales_without_employees_flag,
                        missing_amount_flag = EXCLUDED.missing_amount_flag,
                        ingestion_date = EXCLUDED.ingestion_date

                """
            )
            records = silver_sales_df.to_dict(
                orient= "records"
            )
            with engine.begin() as connection:
                connection.execute(upsert_query,records)

            total += len(silver_sales_df)
        
        logger.info(
            f"[SILVER][SALES] upsert completed | rows={total}"
        )
        
    except Exception as e:
        logger.error(
            f"[SILVER][SALES] load failed | error={e}"
        )


def load_silver_attendance_table():
    logger.info("[SILVER][ATTENDANCE] cleaning started")

    try:
        quary = """
                        SELECT PERCENTILE_CONT(0.5)
                        WITHIN GROUP (ORDER BY attendance_hours) AS median_attendance_hours
                        FROM bronze_attendance
                        WHERE attendance_hours IS NOT NULL;
                    """
        global_attendance_hours_median = pd.read_sql(quary,engine)['median_attendance_hours'].iloc[0]
        silver_attendance_df = pd.read_sql("SELECT * FROM bronze_attendance",engine)
        silver_employee_df = pd.read_sql("SELECT * FROM silver_employees ",engine)

        # >>set data types
        silver_attendance_df["employee_id"] = pd.to_numeric(silver_attendance_df['employee_id'],errors='coerce')
        silver_attendance_df['date'] = pd.to_datetime(silver_attendance_df['date'],errors='coerce')
        silver_attendance_df['attendance_hours'] = pd.to_numeric(silver_attendance_df['attendance_hours'],errors='coerce')

        # >> Handle imposible dates
        silver_attendance_df = silver_attendance_df[
            silver_attendance_df['date'] <= pd.Timestamp.today().normalize()
            ]
        

        # >> Compare with employee_id in silver_employee table and employee_id in bronze_attendance table
        # >> and fix it
        invalid_mask = ~silver_attendance_df['employee_id'].isin(silver_employee_df['employee_id'])
        silver_attendance_df['attendance_without_employees_flag'] = invalid_mask.astype(bool)
        
        # >> Handle missing attendance_hours
        silver_attendance_df['missing_attendance_hours_flag'] = silver_attendance_df['attendance_hours'].isnull().astype(bool)
        silver_attendance_df['attendance_hours'] = silver_attendance_df['attendance_hours'].fillna(global_attendance_hours_median)


        # >> Check impossible attendance_hours
        silver_attendance_df = silver_attendance_df[
            (silver_attendance_df['attendance_hours'] <= 24) & 
            (silver_attendance_df['attendance_hours'] >= 0 )
            ]
        
        # >> Add attendance_status column
        silver_attendance_df['attendance_status'] = (
            silver_attendance_df['attendance_hours'] >= 8 
        ).map({
            True:"FULL_DAY",
            False: "PARTIAL_DAY"
        })
        
        # >> Add overtime column 
        silver_attendance_df['overtime'] = (
            silver_attendance_df['attendance_hours'] - 8
        ).clip(lower= 0)

        silver_attendance_df['ingestion_date'] = pd.Timestamp.now()
        logger.info(
                f"[SILVER][ATTENDANCE] cleaned | rows={len(silver_attendance_df)}"
            )
        
        upsert_query = text("""
                            INSERT INTO silver_attendance(
                                employee_id,
                                date,
                                attendance_hours,
                                attendance_without_employees_flag,
                                missing_attendance_hours_flag,
                                attendance_status,
                                overtime,
                                ingestion_date
                            )
                            VALUES(
                                :employee_id,
                                :date,
                                :attendance_hours,
                                :attendance_without_employees_flag,
                                :missing_attendance_hours_flag,
                                :attendance_status,
                                :overtime,
                                :ingestion_date
                            )
                            ON CONFLICT (employee_id, date)
                            DO UPDATE SET
                                attendance_hours = EXCLUDED.attendance_hours,
                                attendance_without_employees_flag = EXCLUDED.attendance_without_employees_flag,
                                missing_attendance_hours_flag = EXCLUDED.missing_attendance_hours_flag,
                                attendance_status = EXCLUDED.attendance_status,
                                overtime = EXCLUDED.overtime,
                                ingestion_date = EXCLUDED.ingestion_date

                       """)
        records = silver_attendance_df.to_dict(
            orient= "records"
        )
        with engine.begin() as connection:
            connection.execute(upsert_query,records)


        logger.info(
            f"[SILVER][ATTENDANCE] upsert completed | rows={len(records)}"
        )
        
    except Exception as e:
        logger.error(
            f"[SILVER][ATTENDANCE] load failed | error={e}"
        )


    

