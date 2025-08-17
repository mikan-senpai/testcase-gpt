-- Pharmaceutical/Pharmacy POC Database Design
-- SQL Script for MySQL/MariaDB (adjust syntax for other databases)

-- Drop tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS pharmacy_inventory;
DROP TABLE IF EXISTS suppliers;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS medications;
DROP TABLE IF EXISTS medication_categories;
DROP TABLE IF EXISTS user_addresses;
DROP TABLE IF EXISTS user_profiles;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_types;

-- Create user_types table
CREATE TABLE user_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type VARCHAR(50) COMMENT 'patient, doctor, pharmacist, admin',
    permissions VARCHAR(255)
);

-- Create users table
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_type_id INT,
    license_number VARCHAR(100),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    token_google VARCHAR(500),
    token_microsoft VARCHAR(500),
    user_token VARCHAR(500),
    token_expiration DATETIME,
    FOREIGN KEY (user_type_id) REFERENCES user_types(id)
);

-- Create user_profiles table
CREATE TABLE user_profiles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    phone VARCHAR(20),
    date_of_birth DATE,
    insurance_id VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create user_addresses table
CREATE TABLE user_addresses (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    title VARCHAR(50) COMMENT 'Home, Work, Clinic',
    address VARCHAR(255),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create medication_categories table
CREATE TABLE medication_categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category VARCHAR(100) COMMENT 'antibiotic, painkiller, vitamin, cardiac',
    controlled_substance BOOLEAN DEFAULT FALSE
);

-- Create medications table
CREATE TABLE medications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    category_id INT,
    name VARCHAR(255) NOT NULL,
    generic_name VARCHAR(255),
    manufacturer VARCHAR(255),
    strength VARCHAR(50),
    form VARCHAR(50) COMMENT 'tablet, capsule, liquid, injection',
    barcode VARCHAR(100),
    requires_prescription BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (category_id) REFERENCES medication_categories(id)
);

-- Create prescriptions table
CREATE TABLE prescriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT,
    doctor_id INT,
    medication_id INT,
    rx_number VARCHAR(50) UNIQUE,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    duration_days INT,
    refills_allowed INT DEFAULT 0,
    refills_remaining INT DEFAULT 0,
    prescribed_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expiry_date DATETIME,
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (doctor_id) REFERENCES users(id),
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

-- Create suppliers table
CREATE TABLE suppliers (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255),
    api_key VARCHAR(500)
);

-- Create pharmacy_inventory table
CREATE TABLE pharmacy_inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    medication_id INT,
    batch_number VARCHAR(100),
    quantity_available INT DEFAULT 0,
    unit_price DECIMAL(10, 2),
    expiry_date DATE,
    supplier_id INT,
    FOREIGN KEY (medication_id) REFERENCES medications(id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
);

-- Create orders table
CREATE TABLE orders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prescription_id INT,
    patient_id INT,
    pharmacist_id INT,
    status VARCHAR(50) DEFAULT 'pending' COMMENT 'pending, preparing, ready, dispensed',
    total_amount DECIMAL(10, 2),
    insurance_claim_id VARCHAR(100),
    dispensed_date DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
    FOREIGN KEY (patient_id) REFERENCES users(id),
    FOREIGN KEY (pharmacist_id) REFERENCES users(id)
);

-- Create order_items table
CREATE TABLE order_items (
    id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT,
    medication_id INT,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2),
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (medication_id) REFERENCES medications(id)
);

-- Insert sample data for user_types
INSERT INTO user_types (type, permissions) VALUES
('patient', 'view_prescriptions,place_orders'),
('doctor', 'create_prescriptions,view_patients'),
('pharmacist', 'dispense_medications,manage_inventory'),
('admin', 'all');

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_prescriptions_patient ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_doctor ON prescriptions(doctor_id);
CREATE INDEX idx_orders_patient ON orders(patient_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_medications_name ON medications(name);

-- Sample data insertion (optional - uncomment if needed)
/*
-- Insert sample medication categories
INSERT INTO medication_categories (category, controlled_substance) VALUES
('antibiotic', FALSE),
('painkiller', TRUE),
('vitamin', FALSE),
('cardiac', FALSE);

-- Insert sample medications
INSERT INTO medications (category_id, name, generic_name, manufacturer, strength, form, requires_prescription) VALUES
(1, 'Amoxicillin', 'Amoxicillin', 'PharmaCo', '500mg', 'capsule', TRUE),
(2, 'Tylenol', 'Acetaminophen', 'Johnson & Johnson', '500mg', 'tablet', FALSE),
(3, 'Vitamin D3', 'Cholecalciferol', 'NatureMade', '1000IU', 'tablet', FALSE);
*/
