import json
import bcrypt
import mysql.connector
from datetime import timezone
from mysql.connector import pooling
from .utils import resume_score  # Ensure this utility function exists
import streamlit as st
# Database connection pool
db_pool = pooling.MySQLConnectionPool(
    pool_name="resume_parser_pool",
    pool_size=5,
    host="localhost",
    user="root",
    password="root",
    database="resume_parser",
    autocommit=True
)

def create_connection():
    """Create and return a database connection from the pool."""
    try:
        conn = db_pool.get_connection()
        conn.ping(reconnect=True, attempts=3, delay=1)  # Validate and reconnect if necessary
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

def create_session_token(email, token, expires_at):
    """Create a session token for the user."""
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO user_sessions (session_token, email, expires_at)
                VALUES (%s, %s, %s)
            """, (token, email, expires_at.astimezone(timezone.utc).replace(tzinfo=None)))
            conn.commit()
            return True
    except mysql.connector.Error as err:
        print(f"Session error: {err}")
        return False

def get_user_from_session_token(token):
    """Retrieve user details from a session token."""
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                SELECT u.email, u.username FROM user_sessions s
                JOIN users u ON s.email = u.email
                WHERE session_token = %s AND expires_at > UTC_TIMESTAMP()
            """, (token,))
            return cursor.fetchone()
    except mysql.connector.Error as err:
        print(f"Session error: {err}")
        return None

def delete_session_token(token):
    """Delete a session token."""
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("DELETE FROM user_sessions WHERE session_token = %s", (token,))
            conn.commit()
    except mysql.connector.Error as err:
        print(f"Delete error: {err}")

def create_user(email, username, password):
    """Create a new user."""
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor.execute("""
                INSERT INTO users (email, username, password, role_id)
                VALUES (%s, %s, %s, 1)
            """, (email, username, hashed))
            conn.commit()
            return True
    except mysql.connector.Error:
        return False

def verify_user(email, password):
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("SELECT email, username, password, role_id, subscription_type FROM users WHERE email = %s", (email,))
            if user := cursor.fetchone():
                if bcrypt.checkpw(password.encode(), user[2].encode()):
                    return {
                        'status': True,
                        'username': user[1],
                        'role_id': user[3],
                        'subscription_type': user[4]
                    }
                return {'status': False, 'username': None}
    except mysql.connector.Error as err:
        print(f"Auth error: {err}")
        return {'status': False, 'username': None}

def reset_monthly_uploads():
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM resume_analysis
                WHERE subscription_type = 'free'
                AND MONTH(uploaded_at) < MONTH(CURRENT_DATE())
                OR YEAR(uploaded_at) < YEAR(CURRENT_DATE())
            """)
            conn.commit()
    except Exception as e:
        print(f"Error resetting uploads: {e}")
        
def get_upload_count(user_email):
    """Get the number of uploads for the user in the current month."""
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM resume_analysis
                WHERE user_email = %s
                AND MONTH(uploaded_at) = MONTH(CURRENT_DATE())
                AND YEAR(uploaded_at) = YEAR(CURRENT_DATE())
            """, (user_email,))
            result = cursor.fetchone()
            return result[0] if result else 0
    except Exception as e:
        print(f"Error getting upload count: {e}")
        return 0
    
def save_resume_analysis(user_email, parsed_data):
    """Save or update resume analysis data."""
    conn = None
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            # Check if the user exists in the users table
            cursor.execute("SELECT email FROM users WHERE email = %s", (user_email,))
            if not cursor.fetchone():
                st.error("User does not exist in the database.")
                return False

            # Convert numeric fields to strings
            professional_exp = str(parsed_data.get('Professional_Experience_in_Years', '0'))
            score = str(resume_score(parsed_data))  # Ensure resume_score function exists

            # Check if a record already exists for the user
            cursor.execute("""
                SELECT analysis_id FROM resume_analysis 
                WHERE user_email = %s
            """, (user_email,))
            existing_record = cursor.fetchone()

            if existing_record:
                analysis_id = existing_record[0]

                # Update the existing record
                cursor.execute("""
                    UPDATE resume_analysis
                    SET name = %s, parsed_email = %s, applied_profile = %s,
                        professional_experience = %s, resume_score = %s, highest_education = %s,
                        linkedin = %s, github = %s
                    WHERE analysis_id = %s
                """, (
                    parsed_data.get('Name', 'N/A'),
                    parsed_data.get('Email', 'N/A'),
                    parsed_data.get('Applied_for_Profile', 'N/A'),
                    professional_exp,
                    score,
                    parsed_data.get('Highest_Education', 'N/A'),
                    parsed_data.get('LinkedIn', 'N/A'),  # New field
                    parsed_data.get('GitHub', 'N/A'),    # New field
                    analysis_id
                ))

                # Delete related records (phones, addresses, education, work)
                cursor.execute("DELETE FROM phone_numbers WHERE analysis_id = %s", (analysis_id,))
                cursor.execute("DELETE FROM addresses WHERE analysis_id = %s", (analysis_id,))

            else:
                # Insert a new record
                cursor.execute("""
                    INSERT INTO resume_analysis (
                        user_email, name, parsed_email, applied_profile,
                        professional_experience, resume_score, highest_education,
                        linkedin, github
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_email,
                    parsed_data.get('Name', 'N/A'),
                    parsed_data.get('Email', 'N/A'),
                    parsed_data.get('Applied_for_Profile', 'N/A'),
                    professional_exp,
                    score,
                    parsed_data.get('Highest_Education', 'N/A'),
                    parsed_data.get('LinkedIn', 'N/A'),  # New field
                    parsed_data.get('GitHub', 'N/A')     # New field
                ))
                analysis_id = cursor.lastrowid

            # Insert phone number (single value)
            phone = parsed_data.get('Phone_1', 'N/A')
            if phone != 'N/A':
                cursor.execute("""
                    INSERT INTO phone_numbers (analysis_id, phone_number)
                    VALUES (%s, %s)
                """, (analysis_id, phone))

            # Insert address (single value)
            address = parsed_data.get('Address', 'N/A')
            if address != 'N/A':
                cursor.execute("""
                    INSERT INTO addresses (analysis_id, address)
                    VALUES (%s, %s)
                """, (analysis_id, address))

            conn.commit()
            return True
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        if conn:
            conn.rollback()
        return False