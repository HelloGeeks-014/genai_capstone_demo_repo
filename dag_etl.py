from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime

# Define Airflow DAG
default_args = {
    'owner': 'data_engineering_team',
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
}

dag = DAG(
    'monthly_executive_etl',
    default_args=default_args,
    description='Rolls up daily Fact Sales into a Monthly Executive Summary',
    schedule_interval='@monthly',
    catchup=False,
    tags=['aggregate', 'sales', 'monthly']
)

# Lineage: Roll up Fact Sales into Monthly Revenue
aggregate_revenue_insert = """
    INSERT INTO monthly_revenue (report_month, total_revenue, total_items_sold)
    SELECT 
        TO_CHAR(order_date, 'YYYY-MM') AS report_month,
        SUM(total_revenue) AS total_revenue,
        SUM(quantity) AS total_items_sold
    FROM fact_sales
    GROUP BY TO_CHAR(order_date, 'YYYY-MM')
"""

def print_status():
    print("Monthly Revenue updated successfully!")

task_aggregate_revenue = PostgresOperator(
    task_id='load_monthly_revenue',
    sql=aggregate_revenue_insert,
    postgres_conn_id='postgres_prod',
    dag=dag,
)

task_notify = PythonOperator(
    task_id='notify_success',
    python_callable=print_status,
    dag=dag,
)

# Define task dependencies
task_aggregate_revenue >> task_notify
