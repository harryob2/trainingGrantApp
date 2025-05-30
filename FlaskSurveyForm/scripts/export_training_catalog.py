#!/usr/bin/env python3
"""
Export script to extract training_catalog data from SQLite database
and generate SQL INSERT statements for MariaDB production and staging databases.
"""

import sqlite3
import os

def export_training_catalog_data():
    """Export training_catalog data from SQLite to SQL INSERT statements."""
    
    # Database path
    db_path = "training_forms.db"
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found. Please ensure you're running this from the correct directory.")
        return False
    
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get column info to understand the structure
        cursor.execute("PRAGMA table_info(training_catalog)")
        columns_info = cursor.fetchall()
        print("Training catalog table structure:")
        for col in columns_info:
            print(f"  {col[1]} ({col[2]})")
        
        # Get all data from training_catalog table
        cursor.execute("""
            SELECT area, training_name, qty_staff_attending, training_desc, 
                   challenge_lvl, skill_impact, evaluation_method, ida_class, 
                   training_type, training_hours, supplier_name, course_cost
            FROM training_catalog 
            ORDER BY id
        """)
        
        rows = cursor.fetchall()
        
        if not rows:
            print("No data found in training_catalog table.")
            conn.close()
            return False
        
        print(f"Found {len(rows)} records in training_catalog table.")
        
        # Generate SQL INSERT statements
        insert_statements = []
        insert_statements.append("-- Training catalog data exported from local SQLite database")
        insert_statements.append("-- Generated on: " + str(__import__('datetime').datetime.now()))
        insert_statements.append("")
        insert_statements.append("INSERT INTO training_catalog (area, training_name, qty_staff_attending, training_desc, challenge_lvl, skill_impact, evaluation_method, ida_class, training_type, training_hours, supplier_name, course_cost)")
        insert_statements.append("VALUES")
        
        value_lines = []
        for row in rows:
            # Handle NULL values and escape quotes
            escaped_values = []
            for value in row:
                if value is None:
                    escaped_values.append("NULL")
                elif isinstance(value, str):
                    # Escape single quotes for SQL
                    escaped_value = value.replace("'", "''")
                    escaped_values.append(f"'{escaped_value}'")
                else:
                    escaped_values.append(str(value))
            
            value_line = f"    ({', '.join(escaped_values)})"
            value_lines.append(value_line)
        
        # Join all values with commas and newlines
        insert_statements.append(',\n'.join(value_lines))
        insert_statements.append("ON DUPLICATE KEY UPDATE")
        insert_statements.append("    training_desc = VALUES(training_desc),")
        insert_statements.append("    challenge_lvl = VALUES(challenge_lvl),")
        insert_statements.append("    skill_impact = VALUES(skill_impact),")
        insert_statements.append("    evaluation_method = VALUES(evaluation_method),")
        insert_statements.append("    ida_class = VALUES(ida_class),")
        insert_statements.append("    training_type = VALUES(training_type),")
        insert_statements.append("    training_hours = VALUES(training_hours),")
        insert_statements.append("    supplier_name = VALUES(supplier_name),")
        insert_statements.append("    course_cost = VALUES(course_cost);")
        
        # Write to file
        output_file = "scripts/training_catalog_data.sql"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(insert_statements))
        
        print(f"Successfully exported training catalog data to {output_file}")
        print(f"Total records exported: {len(rows)}")
        
        # Also create a CSV for backup
        csv_file = "scripts/training_catalog_export.csv"
        with open(csv_file, 'w', encoding='utf-8') as f:
            # Write header
            f.write("area,training_name,qty_staff_attending,training_desc,challenge_lvl,skill_impact,evaluation_method,ida_class,training_type,training_hours,supplier_name,course_cost\n")
            # Write data
            for row in rows:
                csv_row = []
                for value in row:
                    if value is None:
                        csv_row.append("")
                    elif isinstance(value, str):
                        # Escape quotes for CSV
                        escaped_value = value.replace('"', '""')
                        csv_row.append(f'"{escaped_value}"')
                    else:
                        csv_row.append(str(value))
                f.write(','.join(csv_row) + '\n')
        
        print(f"Also created CSV backup: {csv_file}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    export_training_catalog_data() 