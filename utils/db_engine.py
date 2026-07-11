from sqlalchemy import create_engine,text
import os 
def get_engine():
    
    try :
        db_host = os.environ.get("WAREHOUSE_DB_HOST", "localhost")

        engine = create_engine(f'postgresql://buddhika:password@{db_host}:5432/warehouse')
        return engine
    except Exception as e:
        raise Exception(f"Database Connection Faild!{e}")