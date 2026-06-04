CREATE TABLE users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    created_at TIMESTAMP
);

CREATE TABLE products (
    product_id INT PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    total_amount DECIMAL(10,2),
    order_date TIMESTAMP
);

CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT
);

-- Star Schema Dimension Tables
CREATE TABLE dim_users (
    dim_user_id SERIAL PRIMARY KEY,
    user_id INT,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100)
);

CREATE TABLE dim_products (
    dim_product_id SERIAL PRIMARY KEY,
    product_id INT,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10,2)
);

-- Central Fact Table
CREATE TABLE fact_sales (
    fact_id SERIAL PRIMARY KEY,
    order_date TIMESTAMP,
    user_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    total_revenue DECIMAL(10,2)
);
