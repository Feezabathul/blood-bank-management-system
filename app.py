from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from functools import wraps
from werkzeug.security import check_password_hash
import mysql.connector
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables from .env file (if present)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'blood_bank_super_secret_key_2026')

# MySQL Configuration - Update with your credentials
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'Feeza@2006'),
    'database': os.environ.get('DB_NAME', 'blood_bank')
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# --- Auth Middleware ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'staff_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# --- Template Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, password_hash FROM staff WHERE username = %s", (username,))
            staff = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if staff and check_password_hash(staff['password_hash'], password):
                session['staff_id'] = staff['id']
                session['username'] = username
                return redirect(url_for('donors_page'))
        return "Invalid username or password", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    # If staff is logged in, redirect them to dashboard (public only page)
    if 'staff_id' in session:
        return redirect(url_for('index'))
        
    if session.get('registration_success'):
        return render_template('register.html', already_registered=True)
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        blood_group = request.form.get('blood_group')
        contact = request.form.get('contact')
        height = request.form.get('height')
        weight = request.form.get('weight')
        district = request.form.get('district')
        
        print(f"DEBUG: Form data received -> Name: {full_name}, Age: {age}, Gender: {gender}, Group: {blood_group}, Phone: {contact}, District: {district}, Height: {height}, Weight: {weight}")
        
        if not all([full_name, age, gender, blood_group, contact, district, height, weight]):
            print("DEBUG: Validation failed - Missing fields.")
            return "Error: All fields are required!", 400
            
        conn = get_db_connection()
        if not conn:
            print("DEBUG: Database connection failed.")
            return "Error: Database connection failed", 500
            
        cursor = conn.cursor()
        try:
            query = """
            INSERT INTO donors (full_name, age, gender, height, weight, blood_group, contact, district, registered_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                full_name, 
                age, 
                gender,
                height,
                weight,
                blood_group, 
                contact, 
                district,
                datetime.now().strftime('%Y-%m-%d')
            )
            print(f"DEBUG: Executing SQL Insert...")
            cursor.execute(query, values)
            conn.commit()
            print("DEBUG: Insert successful and committed.")
            
            # Set session variable to prevent immediate duplicate
            session['registration_success'] = True
            
            # Redirect to success page on success
            return redirect(url_for('registration_success_page'))
            
        except Exception as e:
            print(f"DEBUG: SQL Error -> {str(e)}")
            return f"Error registering donor: {str(e)}", 400
        finally:
            cursor.close()
            conn.close()
            
    return render_template('register.html')

@app.route('/registration-success')
def registration_success_page():
    # Only allow access if they just registered successfully
    if not session.get('registration_success'):
        return redirect(url_for('register_page'))
    return render_template('registration_success.html')

@app.route('/donation')
@login_required
def donation_page():
    return render_template('donation.html')

@app.route('/search')
@login_required
def search_page():
    return render_template('search.html')

@app.route('/donors')
@login_required
def donors_page():
    return render_template('donors.html')

# --- API Routes ---

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Total Donors
        cursor.execute("SELECT COUNT(*) as total FROM donors")
        total_donors = cursor.fetchone()['total']
        
        # Donations This Month
        first_day_of_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) as total FROM donations WHERE donation_date >= %s", (first_day_of_month,))
        monthly_donations = cursor.fetchone()['total']
        
        # Blood Group wise count
        cursor.execute("SELECT blood_group, COUNT(*) as count FROM donors GROUP BY blood_group")
        blood_counts = {row['blood_group']: row['count'] for row in cursor.fetchall()}
        
        # Eligible Donors
        # A donor is eligible if they have never donated OR their last donation was >= 90 days ago
        query = """
        SELECT COUNT(*) as total FROM donors d
        LEFT JOIN (
            SELECT donor_id, MAX(donation_date) as last_date
            FROM donations
            GROUP BY donor_id
        ) don ON d.id = don.donor_id
        WHERE don.last_date IS NULL OR don.last_date <= %s
        """
        ninety_days_ago = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
        cursor.execute(query, (ninety_days_ago,))
        eligible_donors = cursor.fetchone()['total']
        
        # Recent Donor Activity (Last 5)
        # Removed as per user request
        
        return jsonify({
            'total_donors': total_donors,
            'monthly_donations': monthly_donations,
            'blood_counts': blood_counts,
            'eligible_donors': eligible_donors
        })
    finally:
        cursor.close()
        conn.close()

@app.route('/api/register', methods=['POST'])
def register_donor():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO donors (full_name, age, gender, height, weight, blood_group, contact, district, registered_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data['full_name'], 
            data['age'], 
            data['gender'], 
            data['height'],
            data['weight'],
            data['blood_group'], 
            data['contact'], 
            data['district'],
            datetime.now().strftime('%Y-%m-%d')
        )
        cursor.execute(query, values)
        conn.commit()
        return jsonify({'message': 'Donor registered successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/api/donors', methods=['GET'])
@login_required
def get_donors():
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetching donors along with last donation date and eligibility
        query = """
        SELECT d.*, don.last_date
        FROM donors d
        LEFT JOIN (
            SELECT donor_id, MAX(donation_date) as last_date
            FROM donations
            GROUP BY donor_id
        ) don ON d.id = don.donor_id
        """
        cursor.execute(query)
        donors = cursor.fetchall()
        
        ninety_days_ago = datetime.now() - timedelta(days=90)
        for donor in donors:
            if donor['last_date'] is None:
                donor['eligible'] = True
                donor['last_date'] = 'Never'
            else:
                last_date = datetime.strptime(str(donor['last_date']), '%Y-%m-%d')
                donor['eligible'] = last_date <= ninety_days_ago
                donor['last_date'] = str(donor['last_date'])
        
        return jsonify(donors)
    finally:
        cursor.close()
        conn.close()

@app.route('/api/donate', methods=['POST'])
@login_required
def record_donation():
    data = request.json
    donor_id = data['donor_id']
    donation_date = data['donation_date']
    units = data['units_donated']
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        # Check last donation
        cursor.execute("SELECT MAX(donation_date) as last_date FROM donations WHERE donor_id = %s", (donor_id,))
        result = cursor.fetchone()
        
        if result and result['last_date']:
            last_date = datetime.strptime(str(result['last_date']), '%Y-%m-%d')
            next_eligible = last_date + timedelta(days=90)
            if datetime.strptime(donation_date, '%Y-%m-%d') < next_eligible:
                return jsonify({
                    'error': 'Ineligible for donation',
                    'next_eligible_date': next_eligible.strftime('%Y-%m-%d')
                }), 400
        
        # Insert donation
        cursor.execute(
            "INSERT INTO donations (donor_id, donation_date, units_donated) VALUES (%s, %s, %s)",
            (donor_id, donation_date, units)
        )
        conn.commit()
        return jsonify({'message': 'Donation recorded successfully!'}), 201
    finally:
        cursor.close()
        conn.close()

@app.route('/api/search', methods=['GET'])
@login_required
def search_donors():
    blood_group = request.args.get('blood_group')
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
        SELECT d.full_name, d.contact, d.blood_group, don.last_date
        FROM donors d
        LEFT JOIN (
            SELECT donor_id, MAX(donation_date) as last_date
            FROM donations
            GROUP BY donor_id
        ) don ON d.id = don.donor_id
        WHERE d.blood_group = %s
        """
        cursor.execute(query, (blood_group,))
        donors = cursor.fetchall()
        
        ninety_days_ago = datetime.now() - timedelta(days=90)
        for donor in donors:
            if donor['last_date'] is None:
                donor['eligible'] = True
                donor['last_date'] = 'Never'
            else:
                last_date = datetime.strptime(str(donor['last_date']), '%Y-%m-%d')
                donor['eligible'] = last_date <= ninety_days_ago
                donor['last_date'] = str(donor['last_date'])
        
        return jsonify(donors)
    finally:
        cursor.close()
        conn.close()

@app.route('/api/delete/<int:donor_id>', methods=['DELETE'])
@login_required
def delete_donor(donor_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'Database connection failed'}), 500
    
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM donors WHERE id = %s", (donor_id,))
        conn.commit()
        return jsonify({'message': 'Donor deleted successfully!'})
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    # Use environment variable for debug mode, defaults to False for production
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=is_debug)
