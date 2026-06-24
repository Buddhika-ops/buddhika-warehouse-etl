# Warehouse ETL Pipeline

This project builds a simple data warehouse pipeline that loads CSV data into PostgreSQL, performs cleaning/transformation in the silver layer, and logs each step in a consistent format.

## Technologies used

- Python
- PostgreSQL
- SQLAlchemy
- pandas
- psycopg2-binary
- Logging for pipeline monitoring

## Project overview

The pipeline currently includes:

- Bronze layer table creation
- Bronze layer data loading from CSV files
- Silver layer cleaning and transformation
- Silver layer UPSERT loading into PostgreSQL
- Structured logging for each stage

## Project structure

- src/bronze - bronze layer loading logic
- src/silver - silver layer cleaning and loading logic
- sql/ - SQL table creation scripts
- utils/ - shared logger utility
- data/ - sample CSV input files

## Setup

1. Create and activate a Python virtual environment
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure PostgreSQL is running locally
4. Update your database connection details in the engine configuration if needed

## Run the pipeline

From the project root:

```bash
python -m src.main
```

## Notes

- The project is designed for local development and testing
- Logs are written to the logs folder
- You may need to create the PostgreSQL database and tables before running the pipeline
