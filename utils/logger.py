import logging
from pathlib import Path


def get_logger(name, layer):
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)


    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(
        log_dir / f"{layer}.log"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger