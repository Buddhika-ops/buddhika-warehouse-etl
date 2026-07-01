CREATE TABLE IF NOT EXISTS gold_dim_employees (
    employee_id      VARCHAR(50)   PRIMARY KEY,
    full_name        VARCHAR(100)  NOT NULL,
    department       VARCHAR(100),
    age              INT,
    experience_years INT,
    monthly_salary   DECIMAL(10, 2),
    city             VARCHAR(100),
    join_date        DATE
);


 CREATE TABLE IF NOT EXISTS gold_workforce_summary (
    department       VARCHAR(100),
    headcount        INT,
    avg_salary       DECIMAL(10, 2),
    min_salary       DECIMAL(10, 2),
    max_salary       DECIMAL(10, 2),
    avg_age          DECIMAL(5, 2),
    avg_experience   DECIMAL(5, 2)
);

 
 CREATE TABLE IF NOT EXISTS gold_salary_bands (
    department     VARCHAR(100),
    band           VARCHAR(20),
    min_salary     DECIMAL(10, 2),
    max_salary     DECIMAL(10, 2),
    avg_salary     DECIMAL(10, 2),
    median_salary  DECIMAL(10, 2),
    employee_count INT
);

 
 CREATE TABLE IF NOT EXISTS gold_attendance_daily (
    employee_id        VARCHAR(50),
    name                VARCHAR(100),
    department          VARCHAR(100),
    date                DATE,
    attendance_hours    DECIMAL(5, 2),
    attendance_status   VARCHAR(20),
    overtime            BOOLEAN,
    ingestion_date      TIMESTAMP,
    PRIMARY KEY (employee_id, date)
);


CREATE TABLE IF NOT EXISTS gold_attendance_monthly (
    employee_id       VARCHAR(50),
    name              VARCHAR(100),
    department        VARCHAR(100),
    year              INT,
    month             INT,
    total_hours       DECIMAL(6, 2),
    overtime_hours    DECIMAL(6, 2),
    days_present      INT,
    days_partial      INT,
    attendance_rate   DECIMAL(5, 2),
    partial_day_rate  DECIMAL(5, 2),
    overtime_rate     DECIMAL(5, 2),
    PRIMARY KEY (employee_id, year, month)
);

CREATE TABLE IF NOT EXISTS gold_overtime_report (
    employee_id     VARCHAR(50),
    name            VARCHAR(100),
    department      VARCHAR(100),
    year            INT,
    month           INT,
    overtime_hours  DECIMAL(6, 2),
    overtime_days   INT,
    overtime_flag   BOOLEAN,
    PRIMARY KEY (employee_id, year, month)
);

CREATE TABLE IF NOT EXISTS gold_sales_by_employee (
    employee_id      VARCHAR(50),
    name             VARCHAR(100),
    department       VARCHAR(100),
    year             INT,
    month            INT,
    total_sales      DECIMAL(12, 2),
    num_orders       INT,
    avg_order_value  DECIMAL(10, 2),
    PRIMARY KEY (employee_id, year, month)
);

 CREATE TABLE IF NOT EXISTS gold_sales_by_employee (
    employee_id      VARCHAR(50),
    name             VARCHAR(100),
    department       VARCHAR(100),
    year             INT,
    month            INT,
    total_sales      DECIMAL(12, 2),
    num_orders       INT,
    avg_order_value  DECIMAL(10, 2),
    PRIMARY KEY (employee_id, year, month)
);

 CREATE TABLE gold_sales_by_product (
    product VARCHAR,
    year INT,
    month INT,
    total_amount DECIMAL(18,2),
    num_sales INT,
    avg_amount DECIMAL(18,2),
    num_employees INT
);
