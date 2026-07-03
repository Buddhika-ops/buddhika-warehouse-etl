import pandas as pd
import logging
from utils.db_engine import get_engine
from src.gold.utils.reader import get_silver_table_reader
from src.gold.utils.writer import write_gold_data_df

engine = get_engine()
logger = logging.getLogger(__name__)


def gold_data_quality_summary():
    try:
        employees_rejected = get_silver_table_reader('silver_employees_rejected',engine=engine)

        attendance_rejected = get_silver_table_reader('silver_attendance_rejected',engine=engine)

        sales_rejected = get_silver_table_reader('silver_sales_rejected',engine=engine)

        dfs = []

        tables = [
            ('employees', employees_rejected),
            ('attendance', attendance_rejected),
            ('sales', sales_rejected)
        ]

        for source_table, df in tables:
            if df.empty:
                continue

            df = df.copy()
            df['source_table'] = source_table

            if 'rejected_at' in df.columns:
                df['load_date'] = pd.to_datetime(df['rejected_at']).dt.date
                
            elif 'ingestion_date' in df.columns:
                df['load_date'] = pd.to_datetime(df['ingestion_date']).dt.date
            else:
                logger.warning(f'[{source_table}] No date column found.')
                continue

            df_agg = (
                df.groupby(
                    ['source_table','rejection_reason','load_date']
                ).agg(
                    rejection_count=('rejection_reason', 'size')
                ).reset_index()
            )

            dfs.append(df_agg)

        if not dfs:
            logger.warning(
                '[gold_data_quality_summary] No rejected data found'
            )
            return

        df_gold = pd.concat(
            dfs,
            ignore_index=True
        )

        df_gold = df_gold.fillna({
            'rejection_count': 0
        })

        df_gold = df_gold[
            [
                'source_table',
                'rejection_reason',
                'rejection_count',
                'load_date'
            ]
        ]

        write_gold_data_df(
            'gold_data_quality_summary',
            df=df_gold,
            engine=engine
        )

        logger.info(
            f'[gold_data_quality_summary] cleaning completed | rows={len(df_gold)}'
        )

    except Exception as e:
        logger.error(
            f'[GOLD BUILD FAILED: gold_data_quality_summary] {e}'
        )
        raise