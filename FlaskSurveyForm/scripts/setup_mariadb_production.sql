-- MariaDB Production Database Setup Script
-- Run this script on your MariaDB server to create the training_tool database and all required tables

-- Create the database
CREATE DATABASE IF NOT EXISTS training_tool CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the new database
USE training_tool;

-- Create training_forms table
CREATE TABLE training_forms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    training_type VARCHAR(255) NOT NULL,
    training_name VARCHAR(255) NOT NULL,
    trainer_name VARCHAR(255),
    trainer_email VARCHAR(255),
    supplier_name VARCHAR(255),
    location_type VARCHAR(255) NOT NULL,
    location_details VARCHAR(255),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    training_hours DECIMAL(10,2),
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    approved BOOLEAN DEFAULT FALSE,
    concur_claim VARCHAR(255),
    course_cost DECIMAL(10,2) DEFAULT 0,
    invoice_number VARCHAR(255),
    training_description TEXT NOT NULL,
    submitter VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ida_class VARCHAR(255),
    INDEX idx_submitter (submitter),
    INDEX idx_submission_date (submission_date),
    INDEX idx_start_date (start_date),
    INDEX idx_approved (approved),
    INDEX idx_training_name (training_name),
    INDEX idx_training_type (training_type),
    INDEX idx_trainer_email (trainer_email)
);

-- Create training_catalog table
CREATE TABLE training_catalog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    area VARCHAR(255),
    training_name VARCHAR(255),
    qty_staff_attending VARCHAR(255),
    training_desc TEXT,
    challenge_lvl VARCHAR(255),
    skill_impact VARCHAR(255),
    evaluation_method VARCHAR(255),
    ida_class VARCHAR(255),
    training_type VARCHAR(255),
    training_hours DECIMAL(10,2),
    supplier_name VARCHAR(255),
    course_cost DECIMAL(10,2) DEFAULT 0,
    INDEX idx_training_name_catalog (training_name),
    INDEX idx_area (area),
    INDEX idx_training_type_catalog (training_type)
);

-- Create attachments table
CREATE TABLE attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    form_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    description TEXT,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE,
    INDEX idx_form_id_attachments (form_id)
);

-- Create admins table
CREATE TABLE admins (
    email VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255)
);

-- Create trainees table
CREATE TABLE trainees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    form_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE,
    INDEX idx_form_id_trainees (form_id),
    INDEX idx_email_trainees (email),
    INDEX idx_department (department)
);

-- Create travel_expenses table
CREATE TABLE travel_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    form_id INT NOT NULL,
    travel_date DATE NOT NULL,
    destination VARCHAR(255) NOT NULL,
    traveler_type VARCHAR(255) NOT NULL COMMENT 'trainer or trainee',
    traveler_email VARCHAR(255) NOT NULL,
    traveler_name VARCHAR(255) NOT NULL,
    travel_mode VARCHAR(255) NOT NULL COMMENT 'mileage, rail, economy_flight',
    cost DECIMAL(10,2) COMMENT 'for rail/flight',
    distance_km DECIMAL(10,2) COMMENT 'for mileage',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE,
    INDEX idx_form_id_travel (form_id),
    INDEX idx_travel_date (travel_date),
    INDEX idx_traveler_email (traveler_email)
);

-- Create material_expenses table
CREATE TABLE material_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    form_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    supplier_name VARCHAR(255) NOT NULL,
    invoice_number VARCHAR(255) NOT NULL,
    material_cost DECIMAL(10,2) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE,
    INDEX idx_form_id_material (form_id),
    INDEX idx_purchase_date (purchase_date)
);

-- Insert default admin users
INSERT INTO admins (email, first_name, last_name) VALUES 
('harry@test.com', 'Harry', 'Test'),
('harry.obrien@stryker.com', 'Harry', 'O''Brien')
ON DUPLICATE KEY UPDATE 
    first_name = VALUES(first_name),
    last_name = VALUES(last_name);

-- Create a user for the application (adjust credentials as needed)
-- Note: You'll need to run these commands as a MySQL admin user
-- CREATE USER IF NOT EXISTS 'training_app'@'%' IDENTIFIED BY 'SecurePassword123!';
-- GRANT ALL PRIVILEGES ON training_tool.* TO 'training_app'@'%';
-- FLUSH PRIVILEGES;

-- Display completion message
SELECT 'Database setup completed successfully!' AS status;
SELECT COUNT(*) AS admin_count FROM admins; 