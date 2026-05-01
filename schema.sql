-- Blood Bank Management System Schema
-- Author: Antigravity AI

CREATE DATABASE IF NOT EXISTS blood_bank;
USE blood_bank;

-- Donors Table
CREATE TABLE IF NOT EXISTS donors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    height INT NOT NULL,
    weight INT NOT NULL,
    blood_group ENUM('A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-') NOT NULL,
    contact VARCHAR(15) NOT NULL,
    district VARCHAR(50) NOT NULL,
    registered_date DATE DEFAULT (CURRENT_DATE)
);

-- Donations Table
CREATE TABLE IF NOT EXISTS donations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    donor_id INT NOT NULL,
    donation_date DATE NOT NULL,
    units_donated INT NOT NULL,
    FOREIGN KEY (donor_id) REFERENCES donors(id) ON DELETE CASCADE
);

-- Staff Table for RBAC
CREATE TABLE IF NOT EXISTS staff (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

-- Sample Data (Optional testing data)
INSERT IGNORE INTO donors (id, full_name, age, gender, height, weight, blood_group, contact, district, registered_date) VALUES
(1, 'Rahul Sharma', 32, 'Male', 175, 70, 'O+', '9876543210', 'Ernakulam', '2026-01-15'),
(2, 'Priya Singh', 28, 'Female', 160, 55, 'A+', '8765432109', 'Thiruvananthapuram', '2026-02-10'),
(3, 'Amit Verma', 45, 'Male', 180, 80, 'B-', '7654321098', 'Kozhikode', '2026-03-01'),
(4, 'Sneha Patel', 24, 'Female', 165, 60, 'AB+', '6543210987', 'Thrissur', '2026-04-10');

INSERT IGNORE INTO donations (donor_id, donation_date, units_donated) VALUES
(1, '2026-01-15', 450),
(2, '2026-02-10', 350),
(3, '2026-03-01', 400);
