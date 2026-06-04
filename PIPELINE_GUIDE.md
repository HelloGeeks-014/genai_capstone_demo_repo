# 📚 Data Engineering Pipeline Guide

Welcome to the internal documentation for our core data engineering pipelines. This document is automatically indexed by our internal RAG systems to help answer engineering, architecture, and design questions.

## 🏗️ Pipeline Architecture & Orchestration

### Orchestration Engine: Apache Airflow
Our entire data ecosystem is orchestrated using Apache Airflow. We leverage Airflow to schedule, execute, and monitor the health of our ETL tasks.

- **DAG Name:** `daily_sales_etl`
- **Schedule:** `@daily` (runs every night at midnight to process the previous day's data)
- **Database Connection:** All tasks use the `postgres_prod` Airflow connection ID to communicate with our production data warehouse.
- **Ownership:** Maintained by the `data_engineering_team`
- **Tags:** `star_schema`, `sales`, `daily`

### Why Postgres?
**"Why did we use Postgres for the metadata DB?"**
We chose Postgres as our primary database for the metadata and analytical backend because of its robust support for JSONB indexing, which is highly critical for tracking our dynamic data lineage graphs and schema definitions. It also provides strong ACID compliance ensuring our data catalog never falls out of sync during concurrent Airflow executions.

---

## 🔀 Data Flow & Star Schema Architecture

To optimize querying performance for our downstream BI tools, we utilize a classic **Kimball Star Schema**. The pipeline extracts from raw normalized tables and loads them into a highly optimized, denormalized hub-and-spoke model.

### 1. Dimension Tables
- **`dim_users`:** Extracts user entity data (names, emails) directly from the raw `users` table.
- **`dim_products`:** Extracts product entity data (categories, pricing) directly from the raw `products` table.

### 2. Central Fact Table (`fact_sales`)
- **Sources:** The fact table denormalizes data by joining `order_items`, `orders`, and `products`.
- **Transformation:** It aggregates the lowest grain of sales data, pulling the `order_date` from `orders`, and calculating `total_revenue` by multiplying `quantity` from `order_items` by the `price` from `products`.
- **Destination:** Loads the combined transactional data directly into `fact_sales`.

---

## ⚙️ Task Dependencies (DAG Structure)

The Airflow DAG executes four distinct tasks designed to safely load the Star Schema.

1. **`load_dim_users`**: Populates `dim_users`.
2. **`load_dim_products`**: Populates `dim_products`.
3. **`load_fact_sales`**: Populates the central `fact_sales` table.
4. **`notify_success`**: Acts as the final downstream gate.

**Dependency Tree:**
```python
[load_dim_users, load_dim_products] >> load_fact_sales >> notify_success
```
This guarantees that the dimension tables are fully populated and updated before we attempt to insert the massive fact records, preventing foreign key violations!

---

## ✓ Data Quality Expectations
- **`dim_users` Table:** Contains highly sensitive PII (`email`). We expect a 0% duplicate rate.
- **`fact_sales` Table:** An immutable ledger. Null values are strictly forbidden in any foreign keys (`user_id`, `product_id`).
