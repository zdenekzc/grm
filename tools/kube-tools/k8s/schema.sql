-- Master / detail: customers -< orders
-- Loaded automatically on first MySQL start via a ConfigMap mounted into
-- /docker-entrypoint-initdb.d/ — the mysql:8 image runs every *.sql file
-- in that directory against the database named by MYSQL_DATABASE.

USE shop;

CREATE TABLE customers (
    id    INT AUTO_INCREMENT PRIMARY KEY,
    name  VARCHAR(100) NOT NULL,
    email VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE orders (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    order_date  DATE NOT NULL,
    total       DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO customers (name, email) VALUES
    ('Jan Novak',      'jan@example.cz'),
    ('Eva Svobodova',  'eva@example.cz'),
    ('Petr Kovar',     'petr@example.cz'),
    ('Marie Cerna',    'marie@example.cz');

INSERT INTO orders (customer_id, order_date, total) VALUES
    (1, '2024-01-15', 1200.00),
    (1, '2024-02-03',  450.50),
    (2, '2024-01-28',  780.00),
    (3, '2024-03-10', 2100.00),
    (3, '2024-03-22',  550.25),
    (3, '2024-04-05',  320.00);
