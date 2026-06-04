# 📚 Data Engineering Pipeline Guide

Welcome to the internal documentation for our core data engineering pipelines. This document is automatically indexed by our internal RAG systems to help answer engineering, architecture, and design questions.

## 🏗️ Pipeline Architecture & Orchestration

### Orchestration Engine: Apache Airflow
Our entire data ecosystem is orchestrated using Apache Airflow. We leverage Airflow to schedule, execute, and monitor the health of our ETL tasks.

- **DAG Name:** `monthly_executive_etl`
- **Schedule:** `@monthly`
- **Database Connection:** All tasks use the `postgres_prod` Airflow connection ID to communicate with our production data warehouse.
- **Ownership:** Maintained by the `data_engineering_team`
- **Tags:** `aggregate`, `sales`, `monthly`

### Why Postgres?
**"Why did we use Postgres for the metadata DB?"**
We chose Postgres as our primary database for the metadata and analytical backend because of its robust support for JSONB indexing, which is highly critical for tracking our dynamic data lineage graphs and schema definitions. It also provides strong ACID compliance ensuring our data catalog never falls out of sync during concurrent Airflow executions.

---

## 🔀 Data Flow & Schema Architecture

Because our raw transactional data natively conforms to a Kimball Star Schema upon ingestion, our downstream Airflow pipeline is dedicated exclusively to producing high-level executive aggregations.

### 1. Native Star Schema (Foundation Layer)
We rely on our core raw tables as our fully-realized Data Warehouse foundation:
- **Dimensions:** `users_data` and `products`.
- **Fact:** `fact_sales` (The raw transactional ledger storing every granular line item and its revenue).

### 2. Executive Aggregate Table (`monthly_revenue`)
- **Sources:** Extracts directly from the foundational `fact_sales` table.
- **Transformation:** It rolls up the granular line items by executing a massive `GROUP BY` operation on the `order_date` (truncated to the month level). It calculates `SUM(total_revenue)` and `SUM(quantity)`.
- **Destination:** Loads the summary metrics into the `monthly_revenue` aggregate table.

---

## ⚙️ Task Dependencies (DAG Structure)

Our Airflow DAG is clean and focused solely on the monthly executive roll-up:

1. **`load_monthly_revenue`**: Extracts from `fact_sales` and populates the `monthly_revenue` table.
2. **`notify_success`**: Acts as the final downstream gate.

**Dependency Tree:**
```python
task_aggregate_revenue >> task_notify
```

---

## ✓ Data Quality Expectations
- **`monthly_revenue` Table:** As an executive dashboard feed, data cannot be missing. If a month has $0 revenue, it must explicitly output $0 rather than omitting the row entirely.
