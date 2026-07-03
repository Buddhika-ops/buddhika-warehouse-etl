from sqlalchemy import create_engine,text

def get_engine():
    
    try :
        engine = create_engine('postgresql://buddhika:password@localhost:5432/warehouse')
        return engine
    except Exception as e:
        raise Exception(f"Database Connection Faild!{e}")