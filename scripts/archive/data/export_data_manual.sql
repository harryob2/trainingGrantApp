-- Manual export script for training_catalog data
-- Run this with: sqlite3 training_forms.db < scripts/export_data_manual.sql > training_catalog_export.txt

.headers on
.mode csv
.output scripts/training_catalog_export.csv

SELECT area, training_name, qty_staff_attending, training_desc, 
       challenge_lvl, skill_impact, evaluation_method, ida_class, 
       training_type, training_hours, supplier_name, course_cost
FROM training_catalog 
ORDER BY id;

.output stdout
.mode list

SELECT 'Exported ' || COUNT(*) || ' training catalog records to scripts/training_catalog_export.csv' AS message
FROM training_catalog; 