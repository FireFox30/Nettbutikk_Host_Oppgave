CREATE DATABASE IF NOT EXISTS nettbutikk;
USE nettbutikk;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    price DECIMAL(10,2),
    image VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(100),
    customer_email VARCHAR(100),
    customer_address TEXT,
    total_price DECIMAL(10,2),
    order_date DATETIME
);

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    product_name VARCHAR(100),
    quantity INT,
    price DECIMAL(10,2),
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id)
);

INSERT INTO products (name, description, price, image) VALUES
('ASUS TUF T500 i5', '13H/16/512/RTX5060 stasjonær gaming-PC', 13999.99, 'ASUS TUF T500 i5.jpg'),
('Razer Ornata', 'V3 RGB Gaming Tastatur', 599.00, 'Razer ornata v3.jpg'),
('Logitech G502 X', 'Gaming Mouse', 829.00, 'Logitech g502.jpg'),
('SteelSeries Aerox 3', 'Wireless Mouse', 789.00, 'Steelseries mouse.jpg'),
('Kingston NV3 2TB', 'NVMe SSD 6000/5000 MB/s', 1899.00, 'Kingston nv3.jpg'),
('AOC 24" 24G42E', 'Full HD Gamingskjerm', 1290.00, 'AOC 24.jpg'),
('Seagate Expansion Portable 2TB', 'Ekstern Harddisk', 995.00, 'Segate 2tb.jpg')
ON DUPLICATE KEY UPDATE id=id;
