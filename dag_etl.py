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
    'daily_sales_etl',
    default_args=default_args,
    description='Extracts daily sales and aggregates them into user and product metrics',
    schedule_interval='@daily',
    catchup=False,
    tags=['metrics', 'sales', 'daily']
)

# Lineage 1: User Metrics
user_metrics_insert = """
    INSERT INTO user_metrics (user_id, total_orders, lifetime_value)
    SELECT 
        u.user_id,
        COUNT(o.order_id) AS total_orders,
        SUM(o.total_amount) AS lifetime_value
    FROM users u
    LEFT JOIN orders o ON u.user_id = o.user_id
    GROUP BY u.user_id
"""

# Lineage 2: Product Metrics
product_metrics_insert = """
    INSERT INTO product_metrics (product_id, total_quantity_sold, total_revenue)
    SELECT 
        p.product_id,
        SUM(oi.quantity) AS total_quantity_sold,
        SUM(oi.quantity * p.price) AS total_revenue
    FROM products p
    JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id
"""

def print_status():
    print("Metrics updated successfully!")

task_user_metrics = PostgresOperator(
    task_id='calculate_user_metrics',
    sql=user_metrics_insert,
    postgres_conn_id='postgres_prod',
    dag=dag,
)

task_product_metrics = PostgresOperator(
    task_id='calculate_product_metrics',
    sql=product_metrics_insert,
    postgres_conn_id='postgres_prod',
    dag=dag,
)

task_notify = PythonOperator(
    task_id='notify_success',
    python_callable=print_status,
    dag=dag,
)

# Define task dependencies
[task_user_metrics, task_product_metrics] >> task_notify
