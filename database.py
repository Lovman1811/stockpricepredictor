import sqlite3
from turtle import st

import pandas as pd
from io import StringIO

# Database Configuration
DATABASE_NAME = "stock_predictions.db"

# Initialize Database
def initialize_db():
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()

    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")  # Enable foreign key support
    c = conn.cursor()

    # Create tables with proper foreign key constraints
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE,
                  password TEXT,
                  email TEXT,
                  full_name TEXT NOT NULL,
                  age INTEGER NOT NULL,
                  phone_no TEXT NOT NULL,
                  aadhar_id TEXT UNIQUE NOT NULL,
                  address TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    c.execute('''CREATE TABLE IF NOT EXISTS predictions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  symbol TEXT,
                  start_date DATE,
                  end_date DATE,
                  forecast_days INTEGER,
                  confidence_level REAL,
                  forecast_data TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')  # Added CASCADE

    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (user_id INTEGER,
                  symbol TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY(user_id, symbol),
                  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE)''')

    conn.commit()
    conn.close()

# User Functions
def create_user(username, password, email, full_name, age, phone_no, aadhar_id, address):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        c.execute('''INSERT INTO users 
                    (username, password, email, full_name, age, phone_no, aadhar_id, address) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                 (username, password, email, full_name, age, phone_no, aadhar_id, address))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Database error: {e}")
        # Handle different constraint violations
        if "username" in str(e):
            st.error("Username already exists!")
        elif "aadhar_id" in str(e):
            st.error("Aadhar ID already registered!")
        elif "email" in str(e):
            st.error("Email already registered!")
        return False
    finally:
        conn.close()

def verify_user(username, password):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if user and user[1] == password:
        return user[0]
    return None

def reset_password(username, new_password):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

def update_user_details(username,  full_name, age, phone_no, address):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''UPDATE users 
                 SET  full_name = ?, age = ?, phone_no = ?, address = ?
                 WHERE username = ?''',
              ( full_name, age, phone_no, address, username))
    conn.commit()
    return True

def get_user_details(username):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("""
        SELECT email, full_name, age, phone_no, aadhar_id, address 
        FROM users 
        WHERE username = ?
    """, (username,))
    rows = c.fetchall()
    conn.close()
    return [
        {
            "email": row[0],
            "full_name": row[1],
            "age": row[2],
            "phone_no": row[3],
            "aadhar_id": row[4],
            "address": row[5]
        } for row in rows
    ]

# Prediction Functions
def save_prediction(user_id, symbol, start_date, end_date, forecast_days, confidence_level, forecast_data):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''INSERT INTO predictions 
                 (user_id, symbol, start_date, end_date, forecast_days, confidence_level, forecast_data)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (user_id, symbol, start_date, end_date, forecast_days, confidence_level, forecast_data.to_json()))
    conn.commit()
    conn.close()

def get_user_predictions(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC''', (user_id,))
    data = c.fetchall()
    conn.close()
    return data

def delete_prediction(prediction_id, user_id):
    """Delete a prediction record"""
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM predictions WHERE id = ? AND user_id = ?", (prediction_id, user_id))
    rows_affected = conn.total_changes
    conn.commit()
    conn.close()
    return rows_affected > 0

# Favorites Functions
def add_favorite(user_id, symbol):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO favorites (user_id, symbol) VALUES (?, ?)", (user_id, symbol))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_favorite(user_id, symbol):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE user_id = ? AND symbol = ?", (user_id, symbol))
    conn.commit()
    conn.close()

def get_favorites(user_id):
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute("SELECT symbol FROM favorites WHERE user_id = ?", (user_id,))
    data = [row[0] for row in c.fetchall()]
    conn.close()
    return data


def delete_user(username):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        c = conn.cursor()
        # Delete user from users table
        c.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        return c.rowcount > 0  # Return True if any rows were affected
    except Exception as e:
        print(f"Error deleting user: {e}")
        conn.rollback()
        return False
