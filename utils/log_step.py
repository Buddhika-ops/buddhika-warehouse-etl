

def log_step(name, before_df, after_df, logger):
    before = len(before_df)
    after = len(after_df)

    logger.info(
        f"[STEP: {name}] "
        f"before={before} | after={after} | dropped={before - after}"
    )