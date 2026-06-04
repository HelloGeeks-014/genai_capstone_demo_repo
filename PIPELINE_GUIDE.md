# 📚 Data Engineering Pipeline Guide

Welcome to the internal documentation for our core data engineering pipelines. This document is automatically indexed by our internal RAG systems to help answer engineering, architecture, and design questions.

## 🏗️ Architecture & Design Decisions

### Why Postgres?
**"Why did we use Postgres for the metadata DB?"**
We chose Postgres as our primary database for the metadata and analytical backend because of its robust support for JSONB indexing, which is highly critical for tracking our dynamic data lineage graphs and schema definitions. It also provides strong ACID compliance ensuring our data catalog never falls out of sync during concurrent Airflow executions.

### Daily Sales ETL (`dag_etl.py`)
Our primary Airflow pipeline is the **Daily Sales ETL**. It is scheduled to run `@daily`.
The primary objective of this pipeline is to extract raw transactional data from the preceding 24 hours, aggregate it into high-level business metrics, and write it to our downstream analytics tables.

## 📊 Data Models

Our data warehouse consists of the following core entities:

1. **`users` Table:** 
   Contains core demographic data. 
   *Note on PII:* This table contains highly sensitive Personally Identifiable Information (PII) including `email` and `phone`. Access to this table is strictly regulated.
2. **`products` Table:**
   Contains product inventory and pricing.
3. **`orders` & `order_items` Tables:**
   Contains immutable transactional ledgers.

## 🔄 Transformations & Lineage

The pipeline executes two primary SQL transformations using the `PostgresOperator`:

### 1. User Metrics
We calculate user lifetime value by joining the `users` table against the `orders` table. We group by the `user_id` to sum the `total_amount` spent across all historical orders. The output is inserted into the `user_metrics` table.

### 2. Product Metrics
To determine which products are performing best, we join the `products` table against `order_items`. We multiply the quantity sold by the unit price to determine total revenue per item, which is inserted into the `product_metrics` table.

## ✓ Data Quality Expectations
We expect the `users` table to have a 0% duplicate rate. However, due to upstream legacy systems, we occasionally see missing (Null) values in the `email` and `phone` columns. We rely on the Data Quality dashboard to monitor these anomalies on a daily basis.
