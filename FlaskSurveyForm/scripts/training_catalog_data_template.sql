-- Training catalog data template
-- Replace the sample data below with your actual training catalog data
-- This file should be run after setting up the production or staging database

-- Example format for INSERT statements:
INSERT INTO training_catalog (area, training_name, qty_staff_attending, training_desc, challenge_lvl, skill_impact, evaluation_method, ida_class, training_type, training_hours, supplier_name, course_cost)
VALUES
    -- Replace these sample rows with your actual data from the CSV export
    ('Sample Area', 'Sample Training Name', '10', 'Sample training description', 'Beginner', 'High', 'Assessment', 'Class A - Legally Required', 'External Training', 8.0, 'Sample Supplier', 1000.00),
    ('Another Area', 'Another Training', '5', 'Another description', 'Intermediate', 'Medium', 'Practical Test', 'Class B - Nat/International Industry Cert', 'Internal Training', 16.0, 'Internal Team', 0.00)
    -- Add more rows as needed, separated by commas
ON DUPLICATE KEY UPDATE 
    training_desc = VALUES(training_desc),
    challenge_lvl = VALUES(challenge_lvl),
    skill_impact = VALUES(skill_impact),
    evaluation_method = VALUES(evaluation_method),
    ida_class = VALUES(ida_class),
    training_type = VALUES(training_type),
    training_hours = VALUES(training_hours),
    supplier_name = VALUES(supplier_name),
    course_cost = VALUES(course_cost);

-- Instructions for manual data entry:
-- 1. Export your training_catalog table data to CSV
-- 2. For each row in the CSV, create a VALUES line above
-- 3. Make sure to:
--    - Escape single quotes by doubling them ('Don''t' for "Don't")
--    - Use NULL for empty values (without quotes)
--    - Quote all text values with single quotes
--    - Don't quote numeric values (training_hours, course_cost)

-- Example of handling special characters:
-- ('IT Training', 'Python & Django Workshop', '15', 'Learn Python programming with Django framework. It''s comprehensive!', 'Advanced', 'High', 'Project-based', 'Class C - Industry Best Practice', 'External Training', 24.0, 'Tech Academy Ltd', 2500.00) 