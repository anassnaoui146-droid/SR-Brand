CREATE DATABASE IF NOT EXISTS divastra_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE divastra_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('customer','admin') NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    name VARCHAR(150) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    old_price DECIMAL(10,2) NULL,
    badge VARCHAR(50) NULL,
    description TEXT NULL,
    sizes VARCHAR(150) NULL,
    image VARCHAR(500) NULL,
    stock INT NOT NULL DEFAULT 0,
    featured TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_products_category (category),
    INDEX idx_products_featured (featured)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    customer_name VARCHAR(100) NOT NULL,
    customer_phone VARCHAR(30) NOT NULL,
    customer_address TEXT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    status ENUM('pending','confirmed','processing','shipped','delivered','cancelled') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_orders_status (status),
    INDEX idx_orders_created_at (created_at)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS newsletter (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) NOT NULL UNIQUE,
    subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    subject VARCHAR(200) NULL,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT IGNORE INTO categories (name) VALUES
('Robes'), ('Ensembles'), ('Accessoires'), ('Nouveautés');

INSERT INTO products (category,name,price,old_price,badge,description,sizes,image,stock,featured)
SELECT * FROM (
  SELECT 'ensembles','Ensemble Premium',299.00,599.00,'BEST SELLER','Décrivez ici votre produit.','S,M,L,XL','',20,1
  UNION ALL SELECT 'robes','Robe Signature',249.00,399.00,'NOUVEAU','Ajoutez votre description produit.','S,M,L','',20,1
  UNION ALL SELECT 'ensembles','Ensemble Satin',319.00,450.00,'-29%','Ajoutez votre description produit.','S,M,L,XL','',15,0
  UNION ALL SELECT 'accessoires','Sac Minimal',179.00,229.00,'ÉDITION','Ajoutez votre description produit.','Unique','',10,0
  UNION ALL SELECT 'robes','Robe Élégance',289.00,399.00,'TENDANCE','Ajoutez votre description produit.','S,M,L','',12,1
  UNION ALL SELECT 'ensembles','Ensemble City',279.00,359.00,'NOUVEAU','Ajoutez votre description produit.','S,M,L,XL','',14,0
  UNION ALL SELECT 'accessoires','Lunettes Chic',149.00,199.00,'','Ajoutez votre description produit.','Unique','',8,0
  UNION ALL SELECT 'robes','Robe Soirée',349.00,499.00,'LIMITÉ','Ajoutez votre description produit.','S,M,L,XL','',6,1
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM products LIMIT 1);


CREATE TABLE contact_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    subject VARCHAR(200),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
