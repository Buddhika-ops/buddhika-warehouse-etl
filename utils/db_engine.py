from pathlib import Path
from sqlalchemy import create_engine, text
import os


def _load_env_file():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_engine():
    try:
        _load_env_file()

        db_host = os.environ.get("WAREHOUSE_DB_HOST", "localhost")
        db_port = os.environ.get("WAREHOUSE_DB_PORT", "5432")
        db_name = os.environ.get("WAREHOUSE_DB_NAME", "warehouse")
        db_user = os.environ.get("WAREHOUSE_DB_USER", "buddhika")
        db_password = os.environ.get("WAREHOUSE_DB_PASSWORD", "password")

        engine = create_engine(
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        return engine
    except Exception as e:
        raise Exception(f"Database Connection Faild!{e}")