-- MariaDB Staging Database Setup Script
-- Run this script on your MariaDB server to create the training_tool_staging database and all required tables
-- This creates an exact replica of the production environment for testing

-- Create the staging database
CREATE DATABASE IF NOT EXISTS training_tool_staging CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the staging database
USE training_tool_staging;

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
    ida_class VARCHAR(255)
);

-- Create trainees table
CREATE TABLE trainees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    form_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    department VARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
);

-- Create travel_expenses table
CREATE TABLE travel_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    form_id INT NOT NULL,
    travel_date DATE NOT NULL,
    destination VARCHAR(255) NOT NULL,
    traveler_type VARCHAR(255) NOT NULL,
    traveler_email VARCHAR(255) NOT NULL,
    traveler_name VARCHAR(255) NOT NULL,
    travel_mode VARCHAR(255) NOT NULL,
    cost DECIMAL(10,2),
    distance_km DECIMAL(10,2),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
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
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
);

-- Create attachments table
CREATE TABLE attachments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    form_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    description VARCHAR(255),
    FOREIGN KEY (form_id) REFERENCES training_forms(id) ON DELETE CASCADE
);

-- Create admins table
CREATE TABLE admins (
    email VARCHAR(255) PRIMARY KEY,
    first_name VARCHAR(255),
    last_name VARCHAR(255)
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
    course_cost DECIMAL(10,2) DEFAULT 0
);

-- Create indexes for performance
CREATE INDEX idx_training_forms_submitter ON training_forms(submitter);
CREATE INDEX idx_training_forms_submission_date ON training_forms(submission_date);
CREATE INDEX idx_training_forms_start_date ON training_forms(start_date);
CREATE INDEX idx_training_forms_approved ON training_forms(approved);
CREATE INDEX idx_training_forms_training_name ON training_forms(training_name);
CREATE INDEX idx_training_forms_training_type ON training_forms(training_type);
CREATE INDEX idx_training_forms_trainer_email ON training_forms(trainer_email);

CREATE INDEX idx_trainees_form_id ON trainees(form_id);
CREATE INDEX idx_trainees_email ON trainees(email);
CREATE INDEX idx_trainees_department ON trainees(department);

CREATE INDEX idx_travel_expenses_form_id ON travel_expenses(form_id);
CREATE INDEX idx_travel_expenses_travel_date ON travel_expenses(travel_date);
CREATE INDEX idx_travel_expenses_traveler_email ON travel_expenses(traveler_email);

CREATE INDEX idx_material_expenses_form_id ON material_expenses(form_id);
CREATE INDEX idx_material_expenses_purchase_date ON material_expenses(purchase_date);

CREATE INDEX idx_attachments_form_id ON attachments(form_id);

CREATE INDEX idx_training_catalog_training_name ON training_catalog(training_name);
CREATE INDEX idx_training_catalog_area ON training_catalog(area);
CREATE INDEX idx_training_catalog_training_type ON training_catalog(training_type);

-- Insert default staging admin users (same as production for testing)
INSERT INTO admins (email, first_name, last_name) VALUES 
('harry@test.com', 'Harry', 'Admin'),
('admin@test.com', 'Test', 'Admin')
ON DUPLICATE KEY UPDATE 
    first_name = VALUES(first_name),
    last_name = VALUES(last_name);

-- Insert sample training catalog data for staging testing
INSERT INTO training_catalog (area, training_name, training_desc, challenge_lvl, skill_impact, ida_class, training_type, training_hours, supplier_name, course_cost) VALUES
('Software Development', 'Python Programming Fundamentals', 'Comprehensive Python programming course covering basics to advanced topics', 'Intermediate', 'High', 'Class B - Nat/International Industry Cert', 'External Training', 16.0, 'Tech Training Corp', 1500.00),
('Quality Management', 'ISO 9001:2015 Implementation', 'Quality management system implementation and maintenance training', 'Advanced', 'High', 'Class A - Legally Required', 'External Training', 24.0, 'Quality Systems Inc', 2000.00),
('Safety Training', 'Workplace Safety Fundamentals', 'Basic workplace safety training and hazard identification', 'Beginner', 'Medium', 'Class A - Legally Required', 'Internal Training', 8.0, 'Internal Safety Team', 0.00),
('Technical Skills', 'CAD Software Training', 'Computer-aided design software training for engineering teams', 'Intermediate', 'High', 'Class C - Industry Best Practice', 'External Training', 40.0, 'Design Software Academy', 2500.00),
('Leadership Development', 'Management Skills Workshop', 'Leadership and management skills development for team leaders', 'Intermediate', 'Medium', 'Class D - Personal Development', 'Internal Training', 12.0, 'HR Development Team', 0.00)
ON DUPLICATE KEY UPDATE 
    training_desc = VALUES(training_desc),
    challenge_lvl = VALUES(challenge_lvl),
    skill_impact = VALUES(skill_impact),
    training_hours = VALUES(training_hours),
    course_cost = VALUES(course_cost);

-- Create staging-specific database user (optional but recommended)
-- Uncomment the following lines if you want a dedicated staging user
-- CREATE USER 'training_staging'@'%' IDENTIFIED BY 'StagingPassword123!';
-- GRANT ALL PRIVILEGES ON training_tool_staging.* TO 'training_staging'@'%';
-- FLUSH PRIVILEGES;

-- Display setup completion message
SELECT 'Staging database setup completed successfully!' as Status,
       'training_tool_staging' as DatabaseName,
       COUNT(*) as AdminUsers
FROM admins;

SELECT 'Training catalog entries created:' as Info, COUNT(*) as CatalogEntries
FROM training_catalog; 