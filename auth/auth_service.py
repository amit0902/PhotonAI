import hashlib
from database.db import get_connection


def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(email, username, password):

    conn = get_connection()
    cur = conn.cursor()

    try:

        cur.execute(
            """
            INSERT INTO users (email, username, password, role)
            VALUES (?, ?, ?, 'user')
            """,
            (email, username, hash_password(password))
        )

        conn.commit()
        return True

    except:
        return False

    finally:
        conn.close()


def authenticate(username, password):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM users
        WHERE username = ? AND password = ?
        """,
        (username, hash_password(password))
    )

    user = cur.fetchone()

    conn.close()

    return user