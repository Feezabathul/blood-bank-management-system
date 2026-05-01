import mysql.connector
import os

try:
    # Connect to MySQL server
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Feeza@2006' # Updated password
    )
    cursor = conn.cursor()
    
    # Read the schema.sql file
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        sql_script = f.read()
        
    # Execute the SQL script
    for result in cursor.execute(sql_script, multi=True):
        pass
        
    conn.commit()
    print("Success! The database and tables have been created successfully.")
    
except mysql.connector.Error as err:
    print(f"MySQL Error: {err}")
    print("Please make sure your MySQL server is running and the password is 'password'.")
except Exception as e:
    print(f"Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'conn' in locals() and conn.is_connected():
        conn.close()
