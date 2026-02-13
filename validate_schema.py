import sqlite3
import os

# Path to database
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'db.sqlite3')

# Define all expected columns for each table
expected_schema = {
    'teachers': {
        'teacher_id': 'INTEGER PRIMARY KEY',
        'user_id': 'INTEGER',
        'name': 'VARCHAR(100)',
        'email': 'VARCHAR(100)',
        'employee_id': 'VARCHAR(50)',
        'department': 'VARCHAR(100)',
        'subject': 'VARCHAR(100)',
        'phone': 'VARCHAR(30)',
        'qualification': 'VARCHAR(255)',
        'experience': 'VARCHAR(255)',
        'dob': 'DATE'
    },
    'students': {
        'student_id': 'INTEGER PRIMARY KEY',
        'user_id': 'INTEGER',
        'name': 'VARCHAR(100)',
        'email': 'VARCHAR(100)',
        'roll_number': 'VARCHAR(50)',
        'department': 'VARCHAR(100)',
        'year_semester': 'VARCHAR(50)',
        'phone': 'VARCHAR(30)',
        'gender': 'VARCHAR(20)',
        'dob': 'DATE',
        'grade': 'VARCHAR(10)'
    },
    'admins': {
        'admin_id': 'INTEGER PRIMARY KEY',
        'user_id': 'INTEGER',
        'name': 'VARCHAR(100)',
        'email': 'VARCHAR(100)',
        'admin_identifier': 'VARCHAR(50)',
        'phone': 'VARCHAR(30)',
        'dob': 'DATE'
    },
    'users': {
        'id': 'INTEGER PRIMARY KEY',
        'username': 'VARCHAR(50)',
        'email': 'VARCHAR(100)',
        'password': 'VARCHAR(255)'
    },
    'roles': {
        'role_id': 'INTEGER PRIMARY KEY',
        'role_name': 'VARCHAR(50)'
    },
    'user_roles': {
        'user_role_id': 'INTEGER PRIMARY KEY',
        'user_id': 'INTEGER',
        'role_id': 'INTEGER'
    },
    'student_progress': {
        'progress_id': 'INTEGER PRIMARY KEY',
        'student_id': 'INTEGER',
        'subject': 'VARCHAR(100)',
        'completion_percentage': 'INTEGER',
        'last_updated': 'DATETIME'
    },
    'student_grades': {
        'grade_id': 'INTEGER PRIMARY KEY',
        'student_id': 'INTEGER',
        'subject': 'VARCHAR(100)',
        'marks': 'FLOAT',
        'total_marks': 'FLOAT',
        'grade': 'VARCHAR(5)'
    },
    'assignments': {
        'assignment_id': 'INTEGER PRIMARY KEY',
        'title': 'VARCHAR(255)',
        'description': 'TEXT',
        'subject': 'VARCHAR(100)',
        'total_marks': 'FLOAT',
        'due_date': 'DATETIME'
    },
    'student_assignments': {
        'student_assignment_id': 'INTEGER PRIMARY KEY',
        'student_id': 'INTEGER',
        'assignment_id': 'INTEGER',
        'score': 'FLOAT',
        'submission_date': 'DATETIME',
        'status': 'VARCHAR(20)'
    },
    'quizzes': {
        'quiz_id': 'INTEGER PRIMARY KEY',
        'title': 'VARCHAR(255)',
        'subject': 'VARCHAR(100)',
        'total_questions': 'INTEGER',
        'total_marks': 'FLOAT'
    },
    'student_quizzes': {
        'student_quiz_id': 'INTEGER PRIMARY KEY',
        'student_id': 'INTEGER',
        'quiz_id': 'INTEGER',
        'score': 'FLOAT',
        'correct_answers': 'INTEGER',
        'attempt_date': 'DATETIME'
    },
    'ai_quiz_attempts': {
        'attempt_id': 'INTEGER PRIMARY KEY',
        'student_id': 'INTEGER',
        'subject': 'VARCHAR(100)',
        'grade_level': 'VARCHAR(50)',
        'question': 'TEXT',
        'correct_answer': 'TEXT',
        'hint': 'TEXT',
        'student_answer': 'TEXT',
        'verdict': 'VARCHAR(20)',
        'feedback': 'TEXT',
        'created_at': 'DATETIME',
        'checked_at': 'DATETIME'
    }
}

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables in database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    print("Database Schema Validation Report\n" + "="*50)
    
    total_added = 0
    
    for table_name, columns in expected_schema.items():
        if table_name not in existing_tables:
            print(f"\n⚠ Table '{table_name}' does not exist")
            continue
        
        # Get existing columns for this table
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = {col[1] for col in cursor.fetchall()}
        
        missing_cols = set(columns.keys()) - existing_cols
        
        if missing_cols:
            print(f"\nTable: {table_name}")
            for col in missing_cols:
                col_type = columns[col].replace('PRIMARY KEY', '').strip()
                print(f"  Adding: {col} ({col_type})...")
                try:
                    cursor.execute(f'ALTER TABLE {table_name} ADD COLUMN {col} {col_type}')
                    total_added += 1
                except Exception as e:
                    print(f"    ✗ Error: {e}")
            conn.commit()
        else:
            print(f"✓ {table_name}")
    
    print(f"\n{'='*50}")
    print(f"✓ Successfully added {total_added} missing column(s)!")
    print(f"Database schema is now up to date.")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")
