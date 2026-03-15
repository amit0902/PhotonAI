import sqlite3
from database.db import get_connection, hash_password


# -----------------------------------------
# Create New User (Signup)
# -----------------------------------------
def create_user(email, username, password, role="user"):

    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    try:

        cur.execute("""
        INSERT INTO users (email, username, password, role)
        VALUES (?, ?, ?, ?)
        """, (email, username, hashed, role))

        conn.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        conn.close()


# -----------------------------------------
# Authenticate Login
# -----------------------------------------
def authenticate_user(username, password):

    conn = get_connection()
    cur = conn.cursor()

    hashed = hash_password(password)

    cur.execute("""
    SELECT username, role
    FROM users
    WHERE username = ? AND password = ?
    """, (username, hashed))

    user = cur.fetchone()

    conn.close()

    if user:

        return {
            "username": user["username"],
            "role": user["role"]
        }

    return None


# -----------------------------------------
# Check if Username Exists
# -----------------------------------------
def username_exists(username):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id FROM users WHERE username = ?
    """, (username,))

    result = cur.fetchone()

    conn.close()

    return result is not None


# -----------------------------------------
# Check if Email Exists
# -----------------------------------------
def email_exists(email):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id FROM users WHERE email = ?
    """, (email,))

    result = cur.fetchone()

    conn.close()

    return result is not None


# -----------------------------------------
# Get All Users (Admin Use)
# -----------------------------------------
def get_all_users():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, email, username, role
    FROM users
    ORDER BY id DESC
    """)

    users = cur.fetchall()

    conn.close()

    return users