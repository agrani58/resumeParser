import json
import bcrypt
import mysql.connector
from datetime import datetime as dt, timedelta, timezone
from mysql.connector import pooling
from app.utils import resume_score
import os

# Database connection pool
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "resume_parser",
    "autocommit": False
}

connection_pool = pooling.MySQLConnectionPool(
    pool_name="resume_pool",
    pool_size=5,
    **db_config
)
##pooling because MYSQL kept crashing""
def get_connection():

    conn = connection_pool.get_connection()
    if not conn.is_connected():
        conn.reconnect(attempts=3, delay=1)
    return conn
def delete_session_token(session_token: str) -> bool:

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM user_sessions 
                    WHERE session_token = %s
                """, (session_token,))
                conn.commit()
                return cursor.rowcount > 0
            
    except Exception as e:
        print(f"Error deleting session token: {e}")
        return False
    return True
def create_session_token(email, token, expires_at):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO user_sessions (session_token, email, expires_at)
                    VALUES (%s, %s, %s)
                """, (token, email, expires_at.astimezone(timezone.utc).replace(tzinfo=None)))
                conn.commit()
                return True
    except mysql.connector.Error as err:
        print(f"Session error: {err}")
        return False

def create_user(email, username, password):

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                # Check if the user has already had a free trial
                cursor.execute("""
                    SELECT COUNT(*) FROM subscriptions 
                    WHERE email = %s AND subscription_type = 'free'
                """, (email,))
                has_free_trial = cursor.fetchone()[0] > 0
                
                if has_free_trial:
                
                    return False
                
                hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                
                cursor.execute("""
                    INSERT INTO users (email, username, password, role_id, signup_date)
                    VALUES (%s, %s, %s, 1, CURRENT_TIMESTAMP)
                """, (email, username, hashed))
                
                #  free trial subscription
                cursor.execute("""
                    INSERT INTO subscriptions 
                    (email, subscription_type, start_date, end_date, is_active)
                    VALUES (%s, 'free', CURRENT_TIMESTAMP, DATE_ADD(CURRENT_TIMESTAMP, INTERVAL 7 DAY), TRUE)
                """, (email,))
                
                conn.commit()
                return True
    except mysql.connector.Error:
        return False

def verify_user(email, password):
    try:
        with get_connection() as conn:
            with conn.cursor(buffered=True) as cursor:
                cursor.execute("SELECT email, username, password, role_id FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if user and bcrypt.checkpw(password.encode(), user[2].encode()):
                    return {'status': True, 'username': user[1], 'role_id': user[3]}
                return {'status': False, 'username': None}
    except mysql.connector.Error as err:
        print(f"Auth error: {err}")
        return {'status': False, 'username': None}
    
def delete_analysis(analysis_ids):
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                
                placeholders = ','.join(['%s'] * len(analysis_ids))
                cursor.execute(
                    f"SELECT DISTINCT user_email FROM resume_analysis "
                    f"WHERE analysis_id IN ({placeholders})",
                    tuple(analysis_ids)
                )
                affected_users = [row[0] for row in cursor.fetchall()]

                # Delete analyses
                cursor.execute(
                    f"DELETE FROM resume_analysis WHERE analysis_id IN ({placeholders})",
                    tuple(analysis_ids)
                )
                
                # Check remaining analyses for affected users
                for user_email in affected_users:
                    cursor.execute(
                        "SELECT COUNT(*) FROM resume_analysis WHERE user_email = %s",
                        (user_email,)
                    )
                    remaining = cursor.fetchone()[0]
                    
                    # Deactivate subscription if no analyses remain
                    if remaining == 0:
                        cursor.execute(
                            "UPDATE subscriptions SET is_active = FALSE "
                            "WHERE email = %s AND is_active = TRUE",
                            (user_email,)
                        )
                
                conn.commit()
                return cursor.rowcount

    except Exception as e:
        print(f"Error deleting analysis: {e}")
        conn.rollback()
        return 0
    
def save_resume_analysis(user_email, parsed_data):

    conn = None
    try:
        conn = get_connection()
        with conn.cursor(buffered=True) as cursor:
            cursor.execute("""
                SELECT signup_date FROM users 
                WHERE email = %s
            """, (user_email,))
            user_data = cursor.fetchone()
            
            if user_data is None:
                raise Exception("User not found. Please check the email address.")
            
            # Check subscription status
            cursor.execute("""
                SELECT subscription_type, start_date FROM subscriptions 
                WHERE email = %s AND is_active = TRUE
            """, (user_email,))
            subscription_data = cursor.fetchone()
            
            if not subscription_data:
                cursor.execute("""
                    INSERT INTO subscriptions (email, subscription_type, start_date, is_active)
                    VALUES (%s, 'free', CURRENT_TIMESTAMP, TRUE)
                """, (user_email,))
                conn.commit()
                trial_end_date = dt.now(timezone.utc) + timedelta(days=7)
            else:
                start_date = dt.now(timezone.utc)
                trial_end_date = start_date + timedelta(days=7)
            
            current_time = dt.now(timezone.utc)
            if subscription_data and subscription_data[0] == 'free' and current_time > trial_end_date:
                raise Exception("Trial period expired. Please upgrade to premium.")
            
            # Convert numeric fields
            professional_exp = str(parsed_data.get('Professional_Experience_in_Years', '0'))
            score = str(resume_score(parsed_data))

            # Check existing analysis
            cursor.execute("""
                SELECT analysis_id FROM resume_analysis 
                WHERE user_email = %s
            """, (user_email,))
            existing_record = cursor.fetchone()

            analysis_id = None
            if existing_record:
                analysis_id = existing_record[0]
                # Delete related records
                cursor.execute("DELETE FROM phone_numbers WHERE analysis_id = %s", (analysis_id,))
                cursor.execute("DELETE FROM addresses WHERE analysis_id = %s", (analysis_id,))
                cursor.execute("DELETE FROM analysis_skills WHERE analysis_id = %s", (analysis_id,))
                
                # Update analysis
                cursor.execute("""
                    UPDATE resume_analysis SET
                        name = %s, parsed_email = %s, applied_profile = %s,
                        professional_experience = %s, resume_score = %s, 
                        highest_education = %s, linkedin = %s, github = %s
                    WHERE analysis_id = %s
                """, (
                    parsed_data.get('Name', 'N/A'),
                    parsed_data.get('Email', 'N/A'),
                    parsed_data.get('Applied_for_Profile', 'N/A'),
                    professional_exp,
                    score,
                    parsed_data.get('Highest_Education', 'N/A'),
                    parsed_data.get('LinkedIn', 'N/A'),
                    parsed_data.get('GitHub', 'N/A'),
                    analysis_id
                ))
            else:
                # Insert new analysis
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
                    parsed_data.get('LinkedIn', 'N/A'),
                    parsed_data.get('GitHub', 'N/A')
                ))
                analysis_id = cursor.lastrowid

            # Insert phone number
            phone = parsed_data.get('Phone_1', 'N/A')
            if phone != 'N/A':
                cursor.execute("""
                    INSERT INTO phone_numbers (analysis_id, phone_number)
                    VALUES (%s, %s)
                """, (analysis_id, phone))

            # Insert address
            address = parsed_data.get('Address', 'N/A')
            if address != 'N/A':
                cursor.execute("""
                    INSERT INTO addresses (analysis_id, address)
                    VALUES (%s, %s)
                """, (analysis_id, address))

            # Process skills
            skills = parsed_data.get('Technical_Skills', [])
            if skills:
                if isinstance(skills, str):
                    skills = [s.strip() for s in skills.split(',') if s.strip()]
                
                for skill in set(skills):
                    cursor.execute("""
                        SELECT skill_id FROM skills 
                        WHERE LOWER(skill_name) = LOWER(%s)
                    """, (skill,))
                    result = cursor.fetchone()
                    if result:
                        skill_id = result[0]
                    else:
                        cursor.execute("INSERT INTO skills (skill_name) VALUES (%s)", (skill,))
                        conn.commit()
                        skill_id = cursor.lastrowid
                    cursor.execute("""
                        INSERT INTO analysis_skills (analysis_id, skill_id)
                        VALUES (%s, %s)
                    """, (analysis_id, skill_id))
            
            conn.commit()
            return True

    except mysql.connector.Error as err:
        if conn:
            conn.rollback()
        print(f"Database error: {err}")
        return False
    finally:
        if conn and conn.is_connected():
            conn.close()