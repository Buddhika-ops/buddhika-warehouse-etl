from src.db_engine import get_engine
from sqlalchemy import text
tables = [
    "silver_employees",
    "silver_employees_rejected",
    "silver_sales",
    "silver_sales_rejected",
    "silver_attendance",
    "silver_attendance_rejected",
]
engine = get_engine()
with engine.connect() as conn:
    for table in tables:
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar()

        print(f"{table}: {count}")