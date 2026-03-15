import sqlite3
import hashlib

DB_PATH = "photonai.db"


# ---------------------------------------------------
# DATABASE CONNECTION
# ---------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------------------------------------------
# PASSWORD HASHING
# ---------------------------------------------------

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# ---------------------------------------------------
# DATABASE INITIALIZATION
# ---------------------------------------------------

def init_db():

    conn = get_connection()
    cur = conn.cursor()

    # ---------------------------------------------------
    # USERS TABLE (Authentication Only)
    # ---------------------------------------------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    """)

    # ---------------------------------------------------
    # SOLAR REQUESTS TABLE (Admin Lead Dashboard)
    # ---------------------------------------------------

    cur.execute("""
    CREATE TABLE IF NOT EXISTS solar_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        city TEXT,
        monthly_units REAL,
        system_kw REAL,
        estimated_price REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ---------------------------------------------------
    # CREATE ADMIN USER IF NOT EXISTS
    # ---------------------------------------------------

    cur.execute("SELECT * FROM users WHERE username = 'admin'")
    admin = cur.fetchone()

    if not admin:

        cur.execute("""
        INSERT INTO users (email, username, password, role)
        VALUES (?, ?, ?, 'admin')
        """, (
            "admin@photonai.com",
            "admin",
            hash_password("admin123")
        ))

    conn.commit()
    conn.close()
