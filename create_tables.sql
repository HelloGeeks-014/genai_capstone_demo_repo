CREATE TABLE users_data (
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
    order_date TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users_data(user_id)
);

-- Central Fact Table (Populated by Airflow ETL)
CREATE TABLE fact_sales (
    fact_id SERIAL PRIMARY KEY,
    order_date TIMESTAMP,
    user_id INT,
    product_id INT,
    quantity INT,
    unit_price DECIMAL(10,2),
    total_revenue DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users_data(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);
