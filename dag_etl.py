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
    description='Extracts daily transactions into a Kimball Star Schema',
    schedule_interval='@daily',
    catchup=False,
    tags=['star_schema', 'sales', 'daily']
)

# Lineage 1: Load Dimension Users
dim_users_insert = """
    INSERT INTO dim_users (user_id, first_name, last_name, email)
    SELECT 
        user_id,
        first_name,
        last_name,
        email
    FROM users
"""

# Lineage 2: Load Dimension Products
dim_products_insert = """
    INSERT INTO dim_products (product_id, name, category, price)
    SELECT 
        product_id,
        name,
        category,
        price
    FROM products
"""

# Lineage 3: Load Fact Sales (Central Hub)
fact_sales_insert = """
    INSERT INTO fact_sales (order_date, user_id, product_id, quantity, unit_price, total_revenue)
    SELECT 
        o.order_date,
        o.user_id,
        oi.product_id,
        oi.quantity,
        p.price AS unit_price,
        (oi.quantity * p.price) AS total_revenue
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    JOIN products p ON oi.product_id = p.product_id
"""

def print_status():
    print("Star Schema updated successfully!")

task_dim_users = PostgresOperator(
    task_id='load_dim_users',
    sql=dim_users_insert,
    postgres_conn_id='postgres_prod',
    dag=dag,
)

task_dim_products = PostgresOperator(
    task_id='load_dim_products',
    sql=dim_products_insert,
    postgres_conn_id='postgres_prod',
    dag=dag,
)

task_fact_sales = PostgresOperator(
    task_id='load_fact_sales',
    sql=fact_sales_insert,
    postgres_conn_id='postgres_prod',
    dag=dag,
)

task_notify = PythonOperator(
    task_id='notify_success',
    python_callable=print_status,
    dag=dag,
)

# Define task dependencies
[task_dim_users, task_dim_products] >> task_fact_sales >> task_notify
