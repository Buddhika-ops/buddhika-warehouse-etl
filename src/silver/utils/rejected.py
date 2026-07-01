import logging

logger = logging.getLogger(__name__) 

def capture_rejected(
    df,
    mask_valid,
    reason,
    reject_table,
    engine 
):
    invalid_rows = df.loc[~mask_valid].copy()

    if invalid_rows.empty:
        invalid_rows['rejected_reason'] = reason
        invalid_rows.to_sql(
            reject_table,
            engine,
            if_exists = 'append',
            index = False
        )
    
    logger.info(
            f"[{reject_table.upper()}] rejected {len(invalid_rows)} rows | reason={reason}"
        )
    
    return df.loc[mask_valid].copy()
