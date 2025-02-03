import bcrypt
import mysql.connector
from datetime import datetime, timezone

def create_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="resume_parser"
    )

def create_session_token(email, token, expires_at):
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
    try:
        with create_connection() as conn, conn.cursor() as cursor:
            cursor.execute("DELETE FROM user_sessions WHERE session_token = %s", (token,))
            conn.commit()
    except mysql.connector.Error as err:
        print(f"Delete error: {err}")

def create_user(email, username, password):
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
            cursor.execute("SELECT email, username, password FROM users WHERE email = %s", (email,))
            if user := cursor.fetchone():
                if bcrypt.checkpw(password.encode(), user[2].encode()):
                    return {'status': True, 'username': user[1]}
                return {'status': False, 'username': None}
            return {'status': False, 'username': None}
    except mysql.connector.Error as err:
        print(f"Auth error: {err}")
        return {'status': False, 'username': None}