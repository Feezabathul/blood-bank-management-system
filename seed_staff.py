import mysql.connector
from werkzeug.security import generate_password_hash

# Config from app.py
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Feeza@2006',
    'database': 'blood_bank'
}

def seed():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # Create staff table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL
    )
    """)
    
    # Check if admin exists
    cursor.execute("SELECT id FROM staff WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed_pw = generate_password_hash('admin123')
        cursor.execute("INSERT INTO staff (username, password_hash) VALUES (%s, %s)", ('admin', hashed_pw))
        conn.commit()
        print("Admin user created successfully.")
    else:
        print("Admin user already exists.")
        
    cursor.close()
    conn.close()

if __name__ == '__main__':
    seed()
