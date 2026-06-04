# 📚 Data Engineering Pipeline Guide

Welcome to the internal documentation for our core data engineering pipelines. This document is automatically indexed by our internal RAG systems to help answer engineering, architecture, and design questions.

## 🏗️ Pipeline Architecture & Orchestration

### Orchestration Engine: Apache Airflow
Our entire data ecosystem is orchestrated using Apache Airflow. We leverage Airflow to schedule, execute, and monitor the health of our ETL tasks.

- **DAG Name:** `daily_sales_etl`
- **Schedule:** `@daily` (runs every night at midnight to process the previous day's data)
- **Database Connection:** All tasks use the `postgres_prod` Airflow connection ID to communicate with our production data warehouse.
- **Ownership:** Maintained by the `data_engineering_team`
- **Tags:** `metrics`, `sales`, `daily`

### Why Postgres?
**"Why did we use Postgres for the metadata DB?"**
We chose Postgres as our primary database for the metadata and analytical backend because of its robust support for JSONB indexing, which is highly critical for tracking our dynamic data lineage graphs and schema definitions. It also provides strong ACID compliance ensuring our data catalog never falls out of sync during concurrent Airflow executions.

---

## 🔀 Data Flow: Sources to Destinations

The primary objective of this pipeline is to extract raw transactional data, aggregate it into high-level business metrics, and write it to our downstream analytics tables.

### 1. User Metrics Flow
- **Sources (Extract):** Reads from the `users` (demographic data) and `orders` (transactional ledger) tables.
- **Transformation:** Joins `users` and `orders` on `user_id`. It groups by user to calculate `total_orders` (count) and `lifetime_value` (sum of total amount).
- **Destination (Load):** Inserts the aggregated rows into the downstream `user_metrics` table.

### 2. Product Metrics Flow
- **Sources (Extract):** Reads from the `products` (inventory/pricing) and `order_items` (line-item transactions) tables.
- **Transformation:** Joins `products` and `order_items` on `product_id`. It multiplies `quantity` by `price` to calculate revenue, and groups by product to sum `total_quantity_sold` and `total_revenue`.
- **Destination (Load):** Inserts the aggregated rows into the downstream `product_metrics` table.

---

## ⚙️ Task Dependencies (DAG Structure)

The Airflow DAG executes three distinct tasks. To optimize performance, the metrics calculations run in parallel.

1. **`calculate_user_metrics`**: A `PostgresOperator` task that executes the user SQL aggregation.
2. **`calculate_product_metrics`**: A `PostgresOperator` task that executes the product SQL aggregation.
3. **`notify_success`**: A `PythonOperator` task that acts as the final downstream gate.

**Dependency Tree:**
```python
[calculate_user_metrics, calculate_product_metrics] >> notify_success
```
This means that `notify_success` will ONLY run if both the user metrics and product metrics tasks successfully complete without errors.

---

## ✓ Data Quality Expectations
- **`users` Table:** Contains highly sensitive PII (`email`, `phone`). We expect a 0% duplicate rate. However, due to upstream legacy systems, we occasionally see missing (Null) values in the email and phone columns. We rely on the Data Quality dashboard to monitor these anomalies on a daily basis.
- **`orders` / `order_items`:** Immutable ledgers. Null values are strictly forbidden in foreign keys (`user_id`, `product_id`).
