# BloodConnect - Premium Blood Bank Management System

A professional full-stack web application designed for efficient blood donor and donation management. Built with a focus on modern healthcare aesthetics and robust data handling.

## 🩸 Features
- **Sophisticated Dashboard**: Real-time stats with animated values and blood group inventory visualization.
- **Donor Registration**: Secure registration with strict validation (Age 18-65) and contact formatting.
- **Intelligent Donation Tracking**: Automated 90-day waiting period enforcement.
- **Smart Search**: Filter donors by blood group with instant eligibility status badges.
- **Premium UI/UX**: Built with Google Font 'Outfit', Glassmorphism, and smooth micro-animations.

## 🛠️ Tech Stack
- **Frontend**: HTML5, Premium CSS (Glassmorphism), Vanilla JavaScript (ES6+).
- **Backend**: Python 3.14+, Flask Framework.
- **Database**: MySQL Server.

---

## 🚀 Getting Started

### 1. Database Configuration
1. Start your **MySQL Server**.
2. Run the `schema.sql` to initialize the database and load **sample data**:
   ```sql
   source schema.sql;
   ```

### 2. Environment Setup
1. Install the required Python libraries:
   ```bash
   pip install flask mysql-connector-python
   ```
2. Open `app.py` and update your MySQL credentials in the `db_config` section:
   ```python
   db_config = {
       'user': 'root',
       'password': 'your_password',
       ...
   }
   ```

### 3. Launching the App
Run the Flask server from your terminal:
```bash
python app.py
```
Open your browser and visit **[http://127.0.0.1:5000](http://127.0.0.1:5000)**.

---

## 📁 Project Structure
- `app.py`: Backend API and routing.
- `schema.sql`: Database definition & sample data.
- `static/`:
    - `styles.css`: Premium medical design system.
    - `script.js`: Interactive frontend logic & animations.
- `templates/`:
    - `base.html`: Modern layout template.
    - `index.html`: Dashboard UI.
    - ... (Other pages)
