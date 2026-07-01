from utils.logger import get_logger
logger = get_logger()

def log_build(table_name, df):
    """Called at the end of every builder — final summary."""
    logger.info(
        f"[GOLD BUILD: {table_name}] "
        f"rows_written={len(df)} | columns={list(df.columns)}"
    )