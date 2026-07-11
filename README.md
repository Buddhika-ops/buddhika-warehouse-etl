# Warehouse ETL

This repository contains an end-to-end data warehouse ETL project that loads CSV-based source data into PostgreSQL, transforms it through bronze, silver, and gold layers, and orchestrates the workflow using Apache Airflow and dbt.

<img width="1191" height="681" alt="Untitled Diagram-Page-2 drawio-2" src="https://github.com/user-attachments/assets/a545eb07-74ce-4090-b294-131f2ec79289" />


## Technologies used

The project uses the following technologies and libraries:

- Python
- PostgreSQL
- SQL
- SQLAlchemy
- pandas
- psycopg2-binary
- Apache Airflow
- Docker Compose
- Redis
- Celery
- dbt with dbt-postgres
- Structured logging


## Project overview

This pipeline is designed around warehouse layering:

- Bronze layer: raw ingestion of CSV files into PostgreSQL
- Silver layer: cleaning, validation, and standardization logic
- Gold layer: curated, analytics-ready datasets
- Orchestration: Airflow DAGs manage the workflow across stages
- Modeling: dbt is used for SQL-based transformation and warehouse modeling

## Project structure

- `airflow_setup/` - Airflow docker-compose setup, DAG files, and runtime logs
- `src/` - Python ETL orchestration and layer-specific processing code
- `sql/` - SQL helper scripts and table creation logic
- `dbt_project/warehouse_dbt/` - dbt project configuration and models
- `data/` - sample source CSV datasets
- `utils/` - shared database and logging utilities
- `scripts/` - helper operational scripts

## Prerequisites

Before running the project, make sure you have:

- Python 3.x installed
- PostgreSQL available locally or through Docker
- Docker Desktop installed for the Airflow stack
- The required Python packages installed in your environment

## Local setup

1. Clone the repository.
2. Create and activate a Python virtual environment.
3. Install the core project dependencies:

```bash
pip install pandas sqlalchemy psycopg2-binary dbt-postgres apache-airflow
```

The Airflow Docker setup also brings in `requests` and `great-expectations` for containerized execution support.

4. Start the Airflow environment with Docker Compose:

```bash
cd airflow_setup
docker compose up -d
```

5. Open the Airflow UI at:

```text
http://localhost:8080
```

6. Update your local database connection settings if your environment differs from the defaults.

## Run the pipeline

You can run the Python entry point from the project root:

```bash
python -m src.main
```

For full orchestration, use the Airflow DAGs defined in the Airflow setup directory.

## Notes

- This project is designed for local development and ETL learning workflows.
- Logs are stored under the project log directories.
- The bronze, silver, and gold layers are intended to be extended into a production-style data warehouse solution.

## What I Learned

- Designing a Medallion Architecture
- Building scalable ETL pipelines
- Data warehouse modeling
- Apache Airflow orchestration
- dbt transformations
- Docker containerization
- PostgreSQL performance optimization
