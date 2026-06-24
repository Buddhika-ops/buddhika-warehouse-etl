import logging
import sys
from pathlib import Path


def get_logger(name="etl_logger", log_file="logs/pipeline.log"):
    project_root = Path(__file__).resolve().parents[1]
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)

    log_path = Path(log_file)
    if not log_path.is_absolute():
        log_path = project_root / log_path

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(module)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger