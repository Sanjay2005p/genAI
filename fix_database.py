import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'db.sqlite3')

# Define expected columns based on the model
expected_columns = {
    'employee_id': 'VARCHAR(50)',
    'department': 'VARCHAR(100)',
    'subject': 'VARCHAR(100)',
    'phone': 'VARCHAR(30)',
    'qualification': 'VARCHAR(255)',
    'dob': 'DATE'
}

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(teachers)")
    existing_columns = {column[1] for column in cursor.fetchall()}
    
    print("Checking teachers table for missing columns...")
    added_count = 0
    
    # Add missing columns
    for col_name, col_type in expected_columns.items():
        if col_name not in existing_columns:
            print(f"Adding {col_name} ({col_type})...")
            cursor.execute(f'''
                ALTER TABLE teachers 
                ADD COLUMN {col_name} {col_type}
            ''')
            added_count += 1
            conn.commit()
        else:
            print(f"✓ {col_name} already exists")
    
    if added_count > 0:
        print(f"\n✓ Successfully added {added_count} missing column(s)!")
    else:
        print("\n✓ All columns already exist!")
    
    # Verify all columns
    cursor.execute("PRAGMA table_info(teachers)")
    columns = cursor.fetchall()
    print("\nCurrent teachers table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
