import uuid
from utils.logger import get_logger
from src.bronze.run_bronze_pipline import bronze_pipeline
from src.silver.run_silver_pipeline import silver_pipline
from src.gold.run_gold_pipeline import gold_pipline
from data.data_generator import attendance,sales


# logger = get_logger()


batch_id = str(uuid.uuid4())

def main():
    # logger.info("[PIPELINE] STARTED")
    try:
        # bronze_pipeline(batch_id)
        # silver_pipline(batch_id)
        # gold_pipline(batch_id)
        # logger.info("[PIPELINE] COMPLETED")
        # employees()
        attendance()
        sales()
    except Exception as e:
        # logger.exception(f"[PIPELINE] FAILED: {e}")
        raise  

if __name__ == "__main__":
    main()