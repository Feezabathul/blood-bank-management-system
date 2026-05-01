import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Feeza@2006',
    'database': 'blood_bank'
}

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        try:
            cursor.execute("ALTER TABLE donors ADD COLUMN height INT NOT NULL AFTER gender")
        except Exception: pass
        
        try:
            cursor.execute("ALTER TABLE donors ADD COLUMN weight INT NOT NULL AFTER height")
        except Exception: pass
        
        # 2. Change address to district
        # Check if address exists first
        cursor.execute("SHOW COLUMNS FROM donors LIKE 'address'")
        if cursor.fetchone():
            cursor.execute("ALTER TABLE donors CHANGE address district VARCHAR(50) NOT NULL")
            print("Successfully migrated address to district.")
            
        print("Database migration completed successfully.")
    except Exception as e:
        print(f"Migration Error: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == '__main__':
    migrate()
